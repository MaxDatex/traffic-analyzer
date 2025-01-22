from enum import Enum


class VehicleState(Enum):
    """Enumeration of possible vehicle states."""

    ARRIVING = "A"
    DEPARTING = "D"
    MOVING = "M"
    PARKED = "P"
    UNKNOWN = "N/A"

    def __str__(self) -> str:
        return self.value
