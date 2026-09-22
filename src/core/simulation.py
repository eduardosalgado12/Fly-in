
from src.models import ZoneType, Graph, Drone
from src.utils import find_path
from typing import Optional
from src.core.visualizer import Visualizer


class Simulation:
    """Routes and runs a fleet of drones from the start to the end zone.

    Computes a space-time path for each drone (via `find_path`), booking
    zone/connection reservations sequentially so later drones avoid
    conflicts with earlier ones, then replays those paths turn by turn in
    `run()`, printing each turn's moves and optionally updating a live
    visualization.
    """

    def __init__(self, nb_drones: int, graph: Graph, visualizer:
                 Optional[Visualizer] = None) -> None:
        """Initializes the simulation and computes every drone's path.

        Args:
            nb_drones: Number of drones to route from start to end.
            graph: The zone graph to route drones through.
            visualizer: Optional `Visualizer` to update after each turn.
                If `None`, the simulation runs without any visual output.
        """
        self.nb_drones = nb_drones
        self.graph = graph
        self.visualizer = visualizer

        self.drones: list[Drone] = []
        self.reservation_zones: dict[tuple[str, int], int] = {}
        self.reservation_connections: dict[tuple[str, str, int], int] = {}

        if self.graph.end is None or self.graph.start is None:
            raise ValueError("Graph has no start or end zone")
        self.end: str = self.graph.end.name
        self.start: str = self.graph.start.name

        self._setup_drones()

    def _setup_drones(self) -> None:
        """Initiate drones, compute space-time paths, and book reservations."""

        for n in range(1, self.nb_drones + 1):
            drone_id = f"D{n}"
            new_drone = Drone(drone_id, self.start)
            self.drones.append(new_drone)

            path = find_path(
                self.graph,
                new_drone.current_zone,
                self.end,
                self.reservation_zones,
                self.reservation_connections
            )
            # print(path)

            if not path:
                raise ValueError(f"No path found for drone {new_drone.id}")
            new_drone.path = path

            for i in range(len(path)):
                zone, turn = path[i]

                atual = self.reservation_zones.get((zone, turn), 0)
                self.reservation_zones[(zone, turn)] = atual + 1

                if i < len(path) - 1:
                    next_zone, _ = path[i + 1]
                    if zone != next_zone:
                        conn_key = (zone, next_zone, turn)
                        atual = self.reservation_connections.get(conn_key, 0)
                        self.reservation_connections[conn_key] = atual + 1

    def run(self) -> None:
        """Execute the turn-by-turn simulation following strictly the
           predefined space-time planning."""
        current_turn = 0
        if self.visualizer is not None:
            self.visualizer.update_drones(self.drones, 0)

        while True:
            # print(self.drones)
            d_end = sum(1 for d in self.drones if d.current_zone == self.end)
            if d_end == self.nb_drones:
                break

            moves: list[str] = []
            current_turn += 1

            for drone in self.drones:
                if (drone.current_zone == self.end and
                   drone.path_step >= len(drone.path) - 1):
                    continue

                curr_zone = drone.current_zone
                next_step = drone.path_step + 1

                if next_step < len(drone.path):
                    next_zone, scheduled_turn = drone.path[next_step]
                    _, curr_scheduled_turn = drone.path[drone.path_step]

                    if scheduled_turn == current_turn:
                        drone.path_step = next_step
                        drone.current_zone = next_zone

                        if next_zone != curr_zone:
                            dest_zone = self.graph.zones[next_zone]

                            if dest_zone.zone_type == ZoneType.RESTRICTED:
                                conn = self.graph.get_connection(
                                    curr_zone, next_zone)
                                if conn:
                                    moves.append(f"{drone.id}-{conn.zone1}-"
                                                 f"{conn.zone2}")
                            else:
                                moves.append(f"{drone.id}-{next_zone}")
                        elif (scheduled_turn != curr_scheduled_turn and
                              self.graph.zones[next_zone].zone_type
                              == ZoneType.RESTRICTED):
                            moves.append(f"{drone.id}-{next_zone}")
            if moves:
                print(" ".join(moves))

            if self.visualizer is not None:
                self.visualizer.update_drones(self.drones, current_turn)
