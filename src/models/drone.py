
SpaceTimePath = list[tuple[str, int]]


class Drone:
    """Represents a single drone moving through the zone graph."""
    def __init__(self, id: str, current_zone: str) -> None:
        """Initializes a drone at its starting zone, with no path yet.

        Args:
            id: Unique identifier for this drone (e.g. "D1").
            current_zone: Name of the zone the drone currently occupies.
        """
        self.id = id
        self.current_zone = current_zone
        self.path: SpaceTimePath = []
        self.path_step: int = 0

    def __repr__(self) -> str:
        return f"Drone({self.id},at={self.current_zone},step={self.path_step})"
