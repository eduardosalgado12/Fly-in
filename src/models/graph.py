
from typing import Optional
from src.models import Zone, StartHub, EndHub


class Connection:
    """Represents a bidirectional connection (edge) between two zones."""
    def __init__(self, zone1: str, zone2: str,
                 max_link_capacity: int = 1) -> None:
        """Initializes a connection between two zones.

        Args:
            zone1: Name of one of the two connected zones.
            zone2: Name of the other connected zone.
            max_link_capacity: Maximum number of drones that may traverse
                this connection simultaneously.
        """
        self.zone1 = zone1
        self.zone2 = zone2
        self.max_link_capacity = max_link_capacity

    def __repr__(self) -> str:
        return f"Connection({self.zone1}-{self.zone2})"

    def connects(self, name_a: str, name_b: str) -> bool:
        """Checks if this connection links the given pair of zone names.

        Args:
            name_a: Name of one zone.
            name_b: Name of the other zone.

        Returns:
            True if this connection links `name_a` and `name_b`, in either
            direction.
        """
        direct = name_a == self.zone1 and name_b == self.zone2
        reverse = name_a == self.zone2 and name_b == self.zone1
        return direct or reverse


class Graph:
    """Represents the full network of zones and connections."""
    def __init__(self) -> None:
        """Initializes an empty graph, with no zones or connections yet."""
        self.zones: dict[str, Zone] = {}
        self.connections: list[Connection] = []
        self.start: Optional[Zone] = None
        self.end: Optional[Zone] = None

    def add_zone(self, new_zone: Zone) -> None:
        """Add zone to the graph, tracking start/end hubs separately.

        Args:
            new_zone: The zone to register in the graph.
        """
        self.zones[new_zone.name] = new_zone

        if isinstance(new_zone, StartHub):
            self.start = new_zone
        elif isinstance(new_zone, EndHub):
            self.end = new_zone

    def add_connection(self, new_connection: Connection) -> None:
        """Add a connection to the graph, rejecting duplicates.

        Args:
            new_connection: The connection to register in the graph.

        Raises:
            ValueError: If either endpoint zone is unknown, or a connection
                between the same two zones already exists.
        """
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
        """Returns the names of zones directly connected to the given zone.

        Args:
            zone_name: Name of the zone whose neighbors to look up.

        Returns:
            A list of zone names directly connected to `zone_name`.
        """
        neighbors: list[str] = []

        for connection in self.connections:
            if connection.zone1 == zone_name:
                neighbors.append(connection.zone2)
            elif connection.zone2 == zone_name:
                neighbors.append(connection.zone1)
        return neighbors

    def get_connection(self, zone1: str, zone2: str) -> Optional[Connection]:
        """Find the connection between two zones within the graph.

        Args:
            zone1: Name of one zone.
            zone2: Name of the other zone.

        Returns:
            The matching `Connection`, or `None` if the two zones are not
            directly connected.
        """
        for conn in self.connections:
            if conn.connects(zone1, zone2):
                return conn
        return None
