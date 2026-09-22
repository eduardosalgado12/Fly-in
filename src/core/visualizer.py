
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from src.models import Graph, Drone, StartHub, EndHub
from typing import Any
import math

HUB_RAD = 0.5
BASE_RAD = 0.2
RAD_PER_DRONE = 0.05
DEFAULT_COLOR = "purple"
OFFSET_RAD = 0.15
PAUSE_SECONDS = 2
DRONE_EMOJI = "✈"


class Visualizer:
    """Draws the zone graph and animates drone positions using matplotlib."""
    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.fig, self.ax = plt.subplots()
        self.drone_markers: list[Any] = []

    def draw_map(self) -> None:
        """Draws all zones and connections once, before the simulation runs."""

        radii: dict[str, float] = {}

        for zone in self.graph.zones.values():
            color = zone.color if zone.color is not None else DEFAULT_COLOR
            desired_radius = (HUB_RAD if isinstance(zone, (StartHub, EndHub))
                              else
                              BASE_RAD + RAD_PER_DRONE * zone.max_drones)
            radius = min(desired_radius, HUB_RAD)
            radii[zone.name] = radius
            circle = Circle((zone.x, zone.y), radius, color=color)
            self.ax.add_patch(circle)
            self.ax.text(zone.x, zone.y - radius - OFFSET_RAD, zone.name,
                         ha='center', va='center', color='black', fontsize=8)

        for conn in self.graph.connections:
            zone1 = self.graph.zones[conn.zone1]
            zone2 = self.graph.zones[conn.zone2]
            dx = zone2.x - zone1.x
            dy = zone2.y - zone1.y
            dist = math.hypot(dx, dy)
            ux, uy = dx / dist, dy / dist

            start_x = zone1.x + ux * radii[zone1.name]
            start_y = zone1.y + uy * radii[zone1.name]
            end_x = zone2.x - ux * radii[zone2.name]
            end_y = zone2.y - uy * radii[zone2.name]

            self.ax.annotate('', xy=(end_x, end_y), xytext=(start_x, start_y),
                             arrowprops=dict(arrowstyle='->', color='gray'))

        pos_x = [zone.x for zone in self.graph.zones.values()]
        pos_y = [zone.y for zone in self.graph.zones.values()]

        self.ax.set_xlim(min(pos_x) - 1, max(pos_x) + 1)
        self.ax.set_ylim(min(pos_y) - 1, max(pos_y) + 1)
        self.ax.set_aspect('equal')
        self.ax.axis('off')

    def update_drones(self, drones: list[Drone], turn: int) -> None:
        """Erases old drone markers and draws new ones at current positions,
        spreading out drones that share a zone."""
        for marker in self.drone_markers:
            marker.remove()

        self.drone_markers = []

        self.ax.set_title(f"Turn {turn}", loc='left')

        groups: dict[str, list[Drone]] = {}
        for drone in drones:
            zone = drone.current_zone
            if zone not in groups:
                groups[zone] = []
            groups[zone].append(drone)

        for zone_name, drones_at_zone in groups.items():
            zone_obj = self.graph.zones[zone_name]
            total = len(drones_at_zone)

            for index, drone in enumerate(drones_at_zone):
                if total == 1:
                    dx, dy = 0.0, 0.0
                else:
                    angle = (2 * math.pi / total) * index
                    dx = OFFSET_RAD * math.cos(angle)
                    dy = OFFSET_RAD * math.sin(angle)

                pos_x = zone_obj.x + dx
                pos_y = zone_obj.y + dy

                marker = self.ax.text(pos_x, pos_y, DRONE_EMOJI, ha='center',
                                      va='center', fontsize=14)
                self.drone_markers.append(marker)

                label = self.ax.text(pos_x, pos_y + OFFSET_RAD, drone.id,
                                     ha='center', va='center', color='black',
                                     fontsize=7, fontweight='bold')
                self.drone_markers.append(label)

        plt.pause(PAUSE_SECONDS)
