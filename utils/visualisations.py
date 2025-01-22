from config.config_handler import DetectorConfig
from models.enums import VehicleState
from ultralytics.utils.plotting import Annotator, colors
import torch
import numpy as np
from typing import Dict, List, Tuple
import cv2


def draw_box_label(
    track_id: int,
    box: torch.Tensor,
    cls: float,
    speed: Dict[int, np.float32],
    names: Dict[int, str],
    baseline: Dict[int, VehicleState],
    annotator: Annotator,
    track_line: List[Tuple[float, float]],
    track_directions: Dict[int, torch.Tensor],
    config: DetectorConfig,
):

    if track_id not in speed:
        speed_label = names[int(cls)]
    elif config.do_analyze:
        speed_label = f"{baseline[track_id]} | {int(speed[track_id])} km/h"
    else:
        speed_label = f"{int(speed[track_id])} km/h"

    annotator.box_label(box, label=speed_label, color=colors(track_id, True))

    if config.draw_tracks:
        annotator.draw_centroid_and_tracks(
            track_line,
            color=colors(int(track_id), True),
            track_thickness=config.line_width,
        )

    if config.draw_direction:
        m = speed[track_id] if (track_id in speed and speed[track_id] > 2) else 0
        center_x = track_line[-1][0]  # (box[0] + box[2]) / 2
        center_y = track_line[-1][1]  # (box[1] + box[3]) / 2
        x_component = -m * np.cos(track_directions[track_id])
        y_component = -m * np.sin(track_directions[track_id])
        new_x = center_x + x_component
        new_y = center_y + y_component

        cv2.arrowedLine(
            annotator.im,
            (int(center_x), int(center_y)),
            (int(new_x), int(new_y)),
            colors(track_id, True),
            config.line_width,
        )
