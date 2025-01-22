import yaml
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DetectorConfig:
    """Configuration settings for the vehicle tracker."""

    # General settings
    base_dir: Path = Path(__file__).parent.parent

    # Model settings
    weights_path: str = base_dir / "weights" / "yolov8s-visdrone.pt"

    # Video settings
    show: bool = True

    # Model settings
    pixel_speed_coef: float = 2.0
    write_every_n_frames: int = 10
    analysis_method: str = "linreg"

    # Visualization settings
    draw_tracks: bool = False
    draw_direction: bool = False
    line_width: int = 2

    # Analysis settings
    do_analyze: bool = True
    slope_threshold: float = 10.0
    speed_threshold: float = 30.0
    parked_speed_threshold: float = 4.0
    abs_mean_threshold: float = 1.0
    min_history_points: int = 5
    correlation_threshold: float = 0.5
    speed_history_window_size: int = 15

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "DetectorConfig":
        """Create config from dictionary."""
        return cls(
            **{k: v for k, v in config_dict.items() if k in cls.__dataclass_fields__}
        )

    def update_from_args(self, args) -> None:
        """Update config with command line arguments."""
        for field in self.__dataclass_fields__:
            if hasattr(args, field) and getattr(args, field) is not None:
                setattr(self, field, getattr(args, field))


def load_config(config_path: str) -> DetectorConfig:
    """Load configuration from YAML file."""
    with open(config_path, "r") as f:
        config_dict = yaml.safe_load(f)
    return DetectorConfig.from_dict(config_dict)


def save_config(config: DetectorConfig, config_path: str) -> None:
    """Save configuration to YAML file."""
    config_dict = {
        field: getattr(config, field)
        for field in config.__dataclass_fields__
        if getattr(config, field) is not None
    }

    with open(config_path, "w") as f:
        yaml.dump(config_dict, f, default_flow_style=False)
