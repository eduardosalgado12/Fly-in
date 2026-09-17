
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

    DEFAULT_MOVEMENT_COST = 1
    RESTRICTED_MOVEMENT_COST = 2

    DEFAULT_ZONE_WEIGHT = 1.0
    PRIORITY_WEIGHT = 0.9

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

    def __repr__(self) -> str:
        return f"Zone({self.name}, {self.zone_type.value})"

    def movement_cost(self) -> int:
        """Returns how many turns it costs to move INTO this zone."""
        if self.zone_type == ZoneType.RESTRICTED:
            return self.RESTRICTED_MOVEMENT_COST
        return self.DEFAULT_MOVEMENT_COST

    def zone_weight(self) -> float:
        """Get the multiplier weight based on the zone type."""

        if self.zone_type == ZoneType.PRIORITY:
            return self.PRIORITY_WEIGHT
        return self.DEFAULT_ZONE_WEIGHT


class StartHub(Zone):
    """Represents the starting zone. Has unlimited capacity."""
    def not_full(self) -> bool:
        return True


class EndHub(Zone):
    """Represents the end zone. Has unlimited capacity."""
    def not_full(self) -> bool:
        return True
