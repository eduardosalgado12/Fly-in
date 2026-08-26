
from classes import Graph, Drone, ZoneType
from collections import deque


class Simulation:

    def __init__(self, nb_drones: int, graph: Graph) -> None:
        self.nb_drones = nb_drones
        self.graph = graph

        self.drones: list[Drone] = []
        for n in range(1, nb_drones + 1):
            drone_id = f"D{n}"
            new_drone = Drone(drone_id, "start")
            self.drones.append(new_drone)
            self.graph.zones["start"].current_occupants.append(new_drone.id)

        if self.graph.end is None:
            raise ValueError("Graph has no end zone")
        self.end_name: str = self.graph.end.name

        for drone in self.drones:
            assert drone.current_zone is not None
            drone.path = self._find_path(drone.current_zone, self.end_name)

    def run(self) -> None:
        """Runs the simulation until all drones reach the end zone."""

        drones_end = 0

        while self.nb_drones != drones_end:
            moves: list[str] = []
            for drone in self.drones:
                if drone.current_zone != self.end_name:
                    next_zone = drone.path[drone.path_step + 1]
                    if self.graph.zones[next_zone].not_full():
                        old_zone = drone.current_zone
                        self.graph.zones[old_zone].current_occupants.remove(drone.id)

                        drone.path_step += 1

                        self.graph.zones[next_zone].current_occupants.append(drone.id)

                        moves.append(f"{drone.id}-{next_zone}")
                    else:
                        pass

            print(" ".join(moves))

            drones_end = 0
            for drone in self.drones:
                if drone.current_zone == self.end_name:
                    drones_end += 1

    def _find_path(self, start: str, end: str) -> list[str]:
        """Finds a path from start to end using breadth-first search."""
        # Caso especial: se o início já for o fim
        if start == end:
            return [start]

        queue = deque([(start, [start])])
        visited = {start}
        while queue:
            (next_zone, path) = queue.popleft()
            for neighbor in self.graph.get_neighbors(next_zone):
                # Ignora zonas bloqueadas ou já visitadas
                if neighbor in visited:
                    continue
                if self.graph.zones[neighbor].zone_type == ZoneType.BLOCKED:
                    continue
                # Se encontrou o destino, retorna imediatamente
                new_path = path + [neighbor]
                if neighbor == end:
                    return new_path
                # Marca como visitado e adiciona à fila
                visited.add(neighbor)
                queue.append((neighbor, new_path))
        return []
