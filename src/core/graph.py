
from typing import Optional
from src.core import Zone, StartHub, EndHub


class Connection:
    """Represents a bidirectional connection (edge) between two zones."""

    def __init__(self, zone1: str, zone2: str,
                 max_link_capacity: int = 1) -> None:
        self.zone1 = zone1
        self.zone2 = zone2
        self.max_link_capacity = max_link_capacity

    def connects(self, name_a: str, name_b: str) -> bool:
        """Checks if this connection links the given pair of zone names."""
        direct = name_a == self.zone1 and name_b == self.zone2
        reverse = name_a == self.zone2 and name_b == self.zone1
        return direct or reverse


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

    def get_connection(self, zone1: str, zone2: str) -> Optional[Connection]:
        """Find the connection between two zones within the graph."""

        for conn in self.connections:
            if conn.connects(zone1, zone2):
                return conn
        return None
