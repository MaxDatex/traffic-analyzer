from dataclasses import dataclass
from typing import Optional

@dataclass
class DetectorConfig:
    """Configuration settings for the vehicle detector."""
    # Analysis settings
    SLOPE_THRESHOLD: float = 10.0
    SPEED_THRESHOLD: float = 30.0
    PARKED_SPEED_THRESHOLD: float = 4.0
    ABS_MEAN_THRESHOLD: float = 1.0
    MIN_HISTORY_POINTS: int = 5
    SPEED_HISTORY_WINDOW_SIZE: int = 15
    CORRELATION_THRESHOLD: float = 0.5
    DO_ANALYZE: bool = True
    
    # Visualization settings
    DRAW_TRACKS: bool = False
    DRAW_DIRECTION: bool = True
    LINE_WIDTH: int = 2
    
    # Processing settings
    WRITE_EVERY_N_FRAMES: int = 10
    PIXEL_SPEED_COEF: float = 2.0
    TREND_ANALYSIS_METHOD: str = 'linreg'