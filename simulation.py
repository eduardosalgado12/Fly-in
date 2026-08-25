
from classes import Graph, Drone, ZoneType
import random


class Simulation:

    def __init__(self, nb_drones: int, graph: Graph) -> None:
        self.nb_drones = nb_drones
        self.graph = graph

        self.drones: list[Drone] = []

        for n in range(1, nb_drones + 1):
            drone_id = f"D{n}"
            new_drone = Drone(drone_id, "start")
            self.drones.append(new_drone)

    def run(self) -> None:
        """Runs the simulation until all drones reach the end zone."""

        drones_end = 0
        while self.nb_drones != drones_end:

            drones_end = 0
            for drone in self.drones:
                if drone.current_zone != self.graph.end.name:

                    neighbors = self.graph.get_neighbors(drone.current_zone)
                    valid_neighbors: list[str] = []
                    for neighbor in neighbors:
                        if self.graph.zones[neighbor].zone_type != ZoneType.BLOCKED:
                            valid_neighbors.append(neighbor)

                    if len(valid_neighbors) > 0:
                        drone.current_zone = random.choice(valid_neighbors)
                    else:
                        pass

                    if drone.current_zone == self.graph.end.name:
                        drones_end += 1

