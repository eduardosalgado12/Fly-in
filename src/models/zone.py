
from enum import Enum
from typing import Optional


class ZoneType(Enum):
    """Enumeration of valid zone types for the drone network."""

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Zone:
    """Represents a single zone (node) in the drone routing graph."""

    def __init__(self, name: str, x: int, y: int,
                 zone_type: ZoneType = ZoneType.NORMAL,
                 color: Optional[str] = None,
                 max_drones: int = 1) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.color = color
        self.max_drones = max_drones

        self.current_occupants: list[str] = []

    def movement_cost(self) -> int:
        """Returns how many turns it costs to move INTO this zone."""
        if self.zone_type == ZoneType.RESTRICTED:
            return 2
        return 1

    def zone_weight(self) -> float:
        if self.zone_type == ZoneType.PRIORITY:
            return 0.9
        return 1.0


class StartHub(Zone):
    """Represents the starting zone. Has unlimited capacity."""

    def not_full(self) -> bool:
        return True


class EndHub(Zone):
    """Represents the end zone. Has unlimited capacity."""

    def not_full(self) -> bool:
        return True
