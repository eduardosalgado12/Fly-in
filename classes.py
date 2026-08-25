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

    def not_full(self) -> bool:
        """Checks if this zone can still accept another drone."""
        return len(self.current_occupants) < self.max_drones


class StartHub(Zone):
    """Represents the starting zone. Has unlimited capacity."""

    def not_full(self) -> bool:
        return True


class EndHub(Zone):
    """Represents the end zone. Has unlimited capacity."""

    def not_full(self) -> bool:
        return True


class Connection:
    """Represents a bidirectional connection (edge) between two zones."""

    def __init__(self, zone1: str, zone2: str,
                 max_link_capacity: int = 1) -> None:
        self.zone1 = zone1
        self.zone2 = zone2
        self.max_link_capacity = max_link_capacity

        self.current_occupants: list[str] = []

    def connects(self, name_a: str, name_b: str) -> bool:
        """Checks if this connection links the given pair of zone names."""
        direct = name_a == self.zone1 and name_b == self.zone2
        reverse = name_a == self.zone2 and name_b == self.zone1
        return direct or reverse

    def not_full(self) -> bool:
        """Checks if this connection can still accept another drone."""

        return len(self.current_occupants) < self.max_link_capacity


class Drone:
    """Represents a single drone moving through the zone graph."""

    def __init__(self, id: str, current_zone: Optional[str] = None,
                 current_connection: Optional[str] = None,
                 turns_remaining: int = 0) -> None:
        self.id = id
        self.current_zone = current_zone
        self.current_connection = current_connection
        self.turns_remaining = turns_remaining


class Graph:
    """Represents the full network of zones and connections."""

    def __init__(self) -> None:
        self.zones: dict[str, Zone] = {}
        self.connections: list[Connection] = []
        self.start: Optional[Zone] = None
        self.end: Optional[Zone] = None

    def add_zone(self, new_zone: Zone) -> None:
        """Add zone to the graph, tracking start/end hubs separately."""

        self.zones[new_zone.name] = new_zone

        if isinstance(new_zone, StartHub):
            self.start = new_zone
        elif isinstance(new_zone, EndHub):
            self.end = new_zone

    def add_connection(self, new_connection: Connection) -> None:
        """Add a connection to the graph, rejecting duplicates."""

        if new_connection.zone1 not in self.zones:
            raise ValueError(f"Unknown zone: {new_connection.zone1}")

        if new_connection.zone2 not in self.zones:
            raise ValueError(f"Unknown zone: {new_connection.zone2}")

        for existing in self.connections:
            if existing.connects(new_connection.zone1, new_connection.zone2):
                raise ValueError(
                    f"Duplicate connection:"
                    f"{new_connection.zone1}-{new_connection.zone2}"
                )

        self.connections.append(new_connection)

    def get_neighbors(self, zone_name: str) -> list[str]:
        """Returns the names of zones directly connected to the given zone."""

        neighbors: list[str] = []

        for connection in self.connections:
            if connection.zone1 == zone_name:
                neighbors.append(connection.zone2)
            elif connection.zone2 == zone_name:
                neighbors.append(connection.zone1)

        return neighbors
