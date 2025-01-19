from core.detector import DirectionDetector
from config.config_handler import DetectorConfig
import cv2
import os

from core.video_processor import process_video


if __name__ == "__main__":
    process_video(
        video_path=os.path.join(DetectorConfig().base_dir, 'assets/videos/day-road-10s.mp4'),
        config=DetectorConfig(),
    )
