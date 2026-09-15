
from typing import Optional


class Drone:
    """Represents a single drone moving through the zone graph."""

    def __init__(self, id: str, current_zone: str,
                 current_connection: Optional[str] = None,
                 turns_remaining: int = 0) -> None:
        self.id = id
        self.current_zone = current_zone
        self.current_connection = current_connection
        self.path: list[tuple[str, int]] = []
        self.path_step: int = 0
