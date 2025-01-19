from typing import List
import numpy as np
from scipy.stats import linregress
from models.enums import VehicleState
from config.config_handler import DetectorConfig

class TrendAnalyzer:
    """Analyzes vehicle movement trends."""
    
    @staticmethod
    def analyze_trend(speeds: List[float], config: DetectorConfig) -> VehicleState:
        """Analyze speed trend to determine vehicle state."""
        if len(speeds) < config.min_history_points:
            return VehicleState.UNKNOWN

        if config.analysis_method == 'linreg':
            x = np.arange(len(speeds))
            slope, _, r_value, _, _ = linregress(x, speeds)
            speed = np.mean(speeds)
            
            if abs(r_value) < config.correlation_threshold:
                return VehicleState.MOVING
                
            if slope > config.slope_threshold and speed < config.speed_threshold:
                return VehicleState.DEPARTING
            elif slope < -config.slope_threshold and speed > config.speed_threshold:
                return VehicleState.ARRIVING
            elif abs(slope) < config.slope_threshold/5 and speed < 2:
                return VehicleState.PARKED
            else:
                return VehicleState.MOVING
                
        if config.analysis_method == 'simple':
            diffs = np.diff(speeds) 
            mean_diff = np.mean(diffs)
            abs_mean_diff = abs(mean_diff)
            positive_diffs = np.sum(diffs > 0)
            negative_diffs = np.sum(diffs < 0)
        
            if positive_diffs > negative_diffs and abs_mean_diff > config.abs_mean_threshold and speed < config.speed_threshold:
                return VehicleState.DEPARTING
            elif positive_diffs < negative_diffs and abs_mean_diff > config.abs_mean_threshold:
                return VehicleState.ARRIVING
            elif abs_mean_diff < config.abs_mean_threshold and speed < config.parked_speed_threshold:
                return VehicleState.PARKED
            else:
                return VehicleState.MOVING
