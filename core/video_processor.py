import cv2
from typing import Optional
from core.detector import DirectionDetector
from config.config_handler import DetectorConfig


def process_video(
    video_path: str,
    config: DetectorConfig,
    output_path: Optional[str] = None,
) -> None:
    """
    Process a video file using the provided detector.

    Args:
        video_path: Path to the input video file
        config: DetectorConfig instance to process frames
        output_path: Optional path to save the processed video
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")

    # Get video properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Initialize video writer if output path is provided
    writer = None
    if output_path:
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    # Initialize detector
    detector = DirectionDetector(config=config, model=config.weights_path)

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print(
                    "Video frame is empty or video processing has been successfully completed."
                )
                break

            # Process frame using detector
            processed_frame, stop = detector.estimate_speed(frame)

            # Write frame if output requested
            if writer:
                writer.write(processed_frame)
            if stop:
                break

    finally:
        cap.release()
        if writer:
            writer.release()
        if config.show:
            cv2.destroyAllWindows()
