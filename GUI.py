from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout, QPushButton, QFileDialog, QStyle
from PyQt5.QtGui import QPixmap, QIcon, QFont
import sys
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QSize, QObject
import numpy as np
from core.detector import DirectionDetector
from config.config_handler import DetectorConfig
import tempfile


class SignalManager(QObject):
    toggle_process_signal = pyqtSignal(bool)


class VideoThread(QThread):
    def __init__(self, video_path, config):
        QThread.__init__(self)
        self.video_path = video_path
        self.config = config
        self.detector = DirectionDetector(config=self.config, model=self.config.weights_path)
        self._run_flag = True
        self.process_enabled = True

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.avi')
        self.temp_video_path = temp_file.name  # Get the temporary file path
        temp_file.close()  # Close the file so it can be used by cv2

        self.fps = 30  # Set default FPS (can adjust dynamically if needed)
        self.frame_width = None
        self.frame_height = None
        self.writer = None  # VideoWriter instance


    change_pixmap_signal = pyqtSignal(np.ndarray)

    def run(self):
        cap = cv2.VideoCapture(self.video_path)

        # Get video properties (for writing)
        if cap.isOpened():
            self.fps = int(cap.get(cv2.CAP_PROP_FPS))
            self.frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # Initialize VideoWriter
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.writer = cv2.VideoWriter(self.temp_video_path, fourcc, self.fps,
                                          (self.frame_width, self.frame_height))
        else:
            print("Error: Unable to open video file.")
            return

        while self._run_flag:
            if not self.process_enabled:
                print("Processing disabled, waiting...")
                while not self.process_enabled:  # Wait until processing is enabled again
                    QThread.msleep(100)  # Sleep for 100ms to avoid busy waiting
                continue  # Skip to the next iteration once processing is enabled

            ret, cv_img = cap.read()
            if not ret:
                print(
                    "Video frame is empty or video processing has been successfully completed."
                )
                break

            processed_frame, stop = self.detector.estimate_speed(cv_img)
            self.change_pixmap_signal.emit(processed_frame)

            # Write processed frame to the video file
            if self.writer:
                self.writer.write(processed_frame)

        cap.release()
        if self.writer:
            self.writer.release()  # Release the VideoWriter when done

    def set_process_enabled(self, enabled):
        self.process_enabled = enabled

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qt live label demo")
        self.disply_width = 640
        self.display_height = 480
        # create the label that holds the image
        self.image_label = QLabel(self)
        self.image_label.resize(self.disply_width, self.display_height)
        # create a text label
        self.textLabel = QLabel('Video')
        self.config = DetectorConfig()
        self.config.show = False
        self.signal_manager = SignalManager()

        btnSize = QSize(16, 16)
        openButton = QPushButton("Open Video")
        openButton.setToolTip("Open Video File")
        openButton.setStatusTip("Open Video File")
        openButton.setFixedHeight(24)
        openButton.setIconSize(btnSize)
        openButton.setFont(QFont("Noto Sans", 8))
        openButton.setIcon(QIcon.fromTheme("document-open", QIcon("D:/_Qt/img/open.png")))
        openButton.clicked.connect(self.abrir)

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setCheckable(True)
        self.playButton.setFixedHeight(24)
        self.playButton.setIconSize(btnSize)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play_pause)

        saveButton = QPushButton("Save Video")
        saveButton.setToolTip("Save the processed video file")
        saveButton.setFixedHeight(24)
        saveButton.setFont(QFont("Noto Sans", 8))
        saveButton.setEnabled(False)  # Only enabled after processing starts
        saveButton.clicked.connect(self.save_video)
        self.saveButton = saveButton

        # create a vertical box layout and add the two labels
        vbox = QVBoxLayout()
        vbox.addWidget(self.image_label)
        vbox.addWidget(openButton)
        vbox.addWidget(self.playButton)
        vbox.addWidget(saveButton)  # Add Save button to the layout
        # set the vbox layout as the widgets layout
        self.setLayout(vbox)

        cv_img = cv2.imread('assets/moving-cars-labeled.jpg')
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)

    def closeEvent(self, event):
        if hasattr(self, "thread"):
            self.thread.stop()
        event.accept()

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def abrir(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Selecciona los mediose",
                                                  ".", "Video Files (*.mp4 *.flv *.ts *.mts *.avi)")

        if fileName != '':
            self.playButton.setEnabled(True)
            self.saveButton.setEnabled(True)  # Enable Save button after video is opened and processing starts
            # create the video capture thread
            self.thread = VideoThread(fileName, self.config)
            # connect its signal to the update_image slot
            self.thread.change_pixmap_signal.connect(self.update_image)
            self.signal_manager.toggle_process_signal.connect(self.thread.set_process_enabled)            # start the thread
            self.thread.start()


    def play_pause(self, checked):
        print("Play/Pause clicked")
        self.signal_manager.toggle_process_signal.emit(checked)  # Emit signal through SignalManager
        if checked:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    a = App()
    a.setWindowTitle("Detector")
    a.resize(500, 500)
    a.show()
    sys.exit(app.exec_())