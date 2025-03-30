from gui.managers import SignalManager
from gui.threads import VideoThread

import os
from PyQt5 import QtGui
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QStyle,
)
from PyQt5.QtGui import QPixmap, QIcon, QFont
import cv2
from PyQt5.QtCore import pyqtSlot, Qt, QSize
import numpy as np
from config.config_handler import DetectorConfig


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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
        self.textLabel = QLabel("Video")
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
        openButton.setIcon(
            QIcon.fromTheme("document-open", QIcon("D:/_Qt/img/open.png"))
        )
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

        cv_img = cv2.imread(os.path.join(PROJECT_ROOT, "assets", "moving-cars-labeled.jpg"))
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)

    def closeEvent(self, event):
        if hasattr(self, "thread"):
            self.thread.stop()
            if (
                self.thread.temp_video_path
            ):  # Delete the temp file if it hasn't been saved
                try:
                    import os

                    os.remove(self.thread.temp_video_path)
                    print("Temporary file deleted.")
                except Exception as e:
                    print(f"Error deleting temp file: {e}")
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
        convert_to_Qt_format = QtGui.QImage(
            rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888
        )
        p = convert_to_Qt_format.scaled(
            self.disply_width, self.display_height, Qt.KeepAspectRatio
        )
        return QPixmap.fromImage(p)

    def abrir(self):
        fileName, _ = QFileDialog.getOpenFileName(
            self,
            "Selecciona los mediose",
            ".",
            "Video Files (*.mp4 *.flv *.ts *.mts *.avi)",
        )

        if fileName != "":
            self.playButton.setEnabled(True)
            self.saveButton.setEnabled(
                True
            )  # Enable Save button after video is opened and processing starts
            # create the video capture thread
            self.thread = VideoThread(fileName, self.config)
            # connect its signal to the update_image slot
            self.thread.change_pixmap_signal.connect(self.update_image)
            self.signal_manager.toggle_process_signal.connect(
                self.thread.set_process_enabled
            )  # start the thread
            self.thread.start()

    def play_pause(self, checked):
        print("Play/Pause clicked")
        self.signal_manager.toggle_process_signal.emit(
            checked
        )  # Emit signal through SignalManager
        if checked:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def save_video(self):
        """Save the processed video file to disk."""
        if hasattr(self, "thread") and self.thread.temp_video_path:
            save_path, _ = QFileDialog.getSaveFileName(
                self, "Save Processed Video", ".", "AVI Files (*.avi)"
            )
            if save_path:
                import shutil

                try:
                    shutil.move(self.thread.temp_video_path, save_path)
                    print(f"Video saved successfully to {save_path}")
                    self.thread.temp_video_path = (
                        None  # Clear temp video path after saving
                    )
                    self.saveButton.setEnabled(
                        False
                    )  # Disable save button after saving
                except Exception as e:
                    print(f"Error saving file: {e}")
