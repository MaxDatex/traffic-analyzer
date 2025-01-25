from typing import Dict, Set, Tuple
import cv2
import numpy as np
from collections import defaultdict


from ultralytics.solutions.solutions import BaseSolution
from ultralytics.utils.plotting import Annotator
from config.config_handler import DetectorConfig
from utils.calculations import calculate_distance, calculate_direction
from utils.visualisations import draw_box_label
from analysis.trend_analyzer import TrendAnalyzer
from time import time


class DirectionDetector(BaseSolution):
    """
    DirectionDetector is a specialized solution for detecting direction, speed, and trends
    of tracked objects in real-time. The class leverages motion tracking data and
    corresponding configurations to process video frames and accurately analyze movement
    patterns of objects. It also provides a visualization layer for displaying results
    during processing.

    The class is designed to compute object speeds using pixel-based measurements, maintain
    historical tracking data, and analyze trends in object movements. Additionally, it offers
    interactivity for users to manipulate the display of objects using mouse events. The
    primary use case for this solution is in video-based object tracking applications where
    directional and speed analysis is required.
    """

    def __init__(self, config: DetectorConfig, **kwargs):
        super().__init__(**kwargs)

        self.speed: Dict[int, float] = dict()  # set for speed data
        self.track_prev_time: Dict[int, float] = dict()  # set for tracks previous time
        self.track_prev_point: Dict[int, Tuple[float, float]] = dict()
        self.track_frame_count: Dict[int, int] = dict()  # previous write frame
        self.track_directions: Dict[int, float] = dict()
        self.baseline: defaultdict = defaultdict(int)
        self.speed_history: defaultdict = defaultdict(list)
        self.selected_boxes: Set[int] = set()
        self.display_everything: bool = True
        self.trend_analyzer: TrendAnalyzer = TrendAnalyzer()
        self.config: DetectorConfig = config

        self.CFG["tracker"] = "BYTETracker"
        self.CFG["verbose"] = False

    def display_output(self, im0):
        if self.config.show and self.env_check:
            cv2.imshow("Maksym Solutions", im0)
            cv2.setMouseCallback("Maksym Solutions", self.mouse_event_for_distance)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                return 1

    def mouse_event_for_distance(self, event, x, y, flags, param):
        """
        Handles mouse events for user interactions with bounding boxes and toggles display settings.

        This method is invoked during mouse events and processes clicks to allow interactions
        with the bounding boxes and control display settings for visualization. Double-clicking
        the left mouse button toggles display settings, single left-click on a bounding box
        adds its associated track ID to the selection, and right-click clears all selections.

        Parameters:
            event (int): The type of mouse event triggered. Uses OpenCV's event constants
                (e.g., cv2.EVENT_LBUTTONDBLCLK, cv2.EVENT_LBUTTONDOWN, cv2.EVENT_RBUTTONDOWN).
            x (int): The x-coordinate of the mouse event position in the window.
            y (int): The y-coordinate of the mouse event position in the window.
        """
        if event == cv2.EVENT_LBUTTONDBLCLK:
            self.display_everything = not self.display_everything
            self.selected_boxes = set()
        elif event == cv2.EVENT_LBUTTONDOWN:
            for box, track_id in zip(self.boxes, self.track_ids):
                if (
                    box[0] < x < box[2]
                    and box[1] < y < box[3]
                    and track_id not in self.selected_boxes
                ):
                    self.selected_boxes.add(track_id)
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.selected_boxes = set()

    def store_speed_history(self, track_id, speed):
        """
        Tracks the speed history for a given track identifier. Updates the history with
        the latest speed value and maintains the configured history window size by
        removing the oldest speed entry when necessary.

        Args:
            track_id (Any): The identifier of the track to associate the speed history with.
            speed (float): The speed value to add to the history for the given track ID.

        Returns:
            None
        """
        self.track_speed_history = self.speed_history[track_id]
        self.track_speed_history.append(speed)
        if len(self.track_speed_history) > self.config.speed_history_window_size:
            self.track_speed_history.pop(0)

    def estimate_speed(self, im0):
        """
        Provides functionality to estimate the object speed based on tracked object data across frames.
        The method processes tracked objects, calculates movement distance and time intervals
        for an estimated speed calculation, tracks historical data necessary for trend analysis,
        and updates annotations on the frames.

        Parameters:
        im0: numpy.ndarray
            The original frame/image from the video input on which the analysis and track annotations will be visualized.

        Returns:
        Tuple[numpy.ndarray, bool]
            The processed frame with annotations and a flag indicating whether to stop further processing.
        """
        self.annotator = Annotator(
            im0, line_width=self.config.line_width
        )  # Initialize annotator
        self.extract_tracks(im0)  # Extract tracks

        for box, track_id, cls in zip(self.boxes, self.track_ids, self.clss):
            if not self.display_everything:
                if track_id not in self.selected_boxes:
                    continue

            self.store_tracking_history(track_id, box)  # Store track history
            if track_id not in self.track_prev_point:
                self.track_prev_point[track_id] = self.track_line[-1]
                self.track_frame_count[track_id] = 0
                self.track_directions[track_id] = 0
                self.track_prev_time[track_id] = 0

            draw_box_label(
                track_id,
                box,
                cls,
                self.speed,
                self.names,
                self.baseline,
                self.annotator,
                self.track_line,
                self.track_directions,
                self.config,
            )

            distance_delta = calculate_distance(
                self.track_line[-1], self.track_prev_point[track_id]
            )
            time_delta = time() - self.track_prev_time[track_id]
            speed = (
                self.config.pixel_speed_coef * (distance_delta / time_delta)
                if time_delta > 0
                else 0
            )
            self.store_speed_history(track_id, speed)

            self.track_frame_count[
                track_id
            ] += 1  # increment previous write frame for the current object
            if self.track_frame_count[track_id] % self.config.write_every_n_frames == 0:
                self.speed[track_id] = np.mean(
                    self.track_speed_history[-self.config.write_every_n_frames :]
                )
                self.baseline[track_id] = self.trend_analyzer.analyze_trend(
                    self.track_speed_history[-self.config.write_every_n_frames :],
                    self.config,
                )

                self.track_directions[track_id] = calculate_direction(
                    self.track_line[-1], self.track_line[0]
                )

                self.track_frame_count[track_id] = 0
                self.track_prev_time[track_id] = time()
                self.track_prev_point[track_id] = self.track_line[-1]

        stop = self.display_output(im0)

        return im0, stop  # return output image for more usage
