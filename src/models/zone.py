
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
        """Initializes a zone.

        Args:
            name: Unique identifier for this zone.
            x: X coordinate of this zone, used for its visual position.
            y: Y coordinate of this zone, used for its visual position.
            zone_type: The zone's type, which determines its movement cost
                and behaviour.
            color: Optional color used for visual representation.
            max_drones: Maximum number of drones that may occupy this zone
                simultaneously.
        """
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.color = color
        self.max_drones = max_drones

    def __repr__(self) -> str:
        return f"Zone({self.name}, {self.zone_type.value})"

    def movement_cost(self) -> int:
        """Returns how many turns it costs to move INTO this zone.

        Returns:
            2 for a `RESTRICTED` zone, 1 for any other zone type.
        """
        if self.zone_type == ZoneType.RESTRICTED:
            return self.RESTRICTED_MOVEMENT_COST
        return self.DEFAULT_MOVEMENT_COST

    def zone_weight(self) -> float:
        """Get the multiplier weight based on the zone type.

        Returns:
            A weight slightly below 1.0 for a `PRIORITY` zone (making it
            marginally cheaper in the pathfinder), 1.0 for any other zone
            type.
        """
        if self.zone_type == ZoneType.PRIORITY:
            return self.PRIORITY_WEIGHT
        return self.DEFAULT_ZONE_WEIGHT


class StartHub(Zone):
    """Represents the starting zone. Has unlimited capacity."""


class EndHub(Zone):
    """Represents the end zone. Has unlimited capacity."""
