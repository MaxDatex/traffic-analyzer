from PyQt5.QtCore import pyqtSignal, QThread
from core.detector import DirectionDetector
import tempfile
import cv2
import numpy as np


class VideoThread(QThread):
    def __init__(self, video_path, config):
        QThread.__init__(self)
        self.video_path = video_path
        self.config = config
        self.detector = DirectionDetector(
            config=self.config, model=self.config.weights_path
        )
        self._run_flag = True
        self.process_enabled = True

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".avi")
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
            fourcc = cv2.VideoWriter_fourcc(*"XVID")
            self.writer = cv2.VideoWriter(
                self.temp_video_path,
                fourcc,
                self.fps,
                (self.frame_width, self.frame_height),
            )
        else:
            print("Error: Unable to open video file.")
            return

        while self._run_flag:
            if not self.process_enabled:
                print("Processing disabled, waiting...")
                while (
                    not self.process_enabled
                ):  # Wait until processing is enabled again
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
