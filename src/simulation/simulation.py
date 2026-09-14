
from graph.classes import ZoneType, Graph, Drone
from pathfinding.dijkstra import find_path


class Simulation:

    def __init__(self, nb_drones: int, graph: Graph) -> None:
        self.nb_drones = nb_drones
        self.graph = graph

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

            path = find_path(new_drone.current_zone, self.end)

            if not path:
                raise ValueError(f"No path found for drone {new_drone.id}")
            new_drone.path = path

            # Commit chronological reservations for the drone
            for i in range(len(path)):
                zone, turn = path[i]

                # 1. Book the Zone
                self.reservation_zones[(zone, turn)] = self.reservation_zones.get((zone, turn), 0) + 1

                # 2. Book the Connection if there is a next step and the drone actually moves
                if i < len(path) - 1:
                    next_zone, next_turn = path[i + 1]
                    if zone != next_zone:
                        conn_key = (zone, next_zone, next_turn)
                        self.reservation_connections[conn_key] = self.reservation_connections.get(conn_key, 0) + 1

    def run(self) -> None:
        """Execute the turn-by-turn simulation following strictly the
           predefined space-time planning."""
        current_turn = 0

        while True:
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

                    if scheduled_turn == current_turn:
                        drone.path_step = next_step
                        drone.current_zone = next_zone

                        if next_zone != curr_zone:
                            dest_zone = self.graph.zones[next_zone]

                            if dest_zone.zone_type == ZoneType.RESTRICTED:
                                conn = self.graph.get_connection(curr_zone, next_zone)

                                if conn:
                                    moves.append(f"{drone.id}-{conn.zone1}-{conn.zone2}")
                            else:
                                moves.append(f"{drone.id}-{next_zone}")
            if moves:
                print(" ".join(moves))
