import numpy as np
from typing import Tuple
from scipy.stats import linregress


def calculate_distance(start: Tuple[float, float], end: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points."""
    return np.sqrt(pow((end[0] - start[0]), 2) + pow((end[1] - start[1]), 2))


def calculate_direction(start: Tuple[float, float], end: Tuple[float, float]) -> float:
    """Calculate direction angle between two points."""
    return np.arctan2(end[1] - start[1], end[0] - start[0])
