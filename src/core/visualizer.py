
import matplotlib.pyplot as plt  # type: ignore
from src.models import Graph

DEFAULT_COLOR = "purple"


class Visualizer:
    """Draws the zone graph and animates drone positions using matplotlib."""
    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.fig, self.ax = plt.subplots()

    def draw_map(self) -> None:
        """Draws all zones and connections once, before the simulation runs."""
        for zone in self.graph.zones.values():
            color = zone.color if zone.color is not None else DEFAULT_COLOR
            circle = plt.Circle((zone.x, zone.y), 0.3, color=color)
            self.ax.add_patch(circle)
            self.ax.text(zone.x, zone.y, zone.name, ha='center',
                         va='center', color='black', fontsize=8)

        for conn in self.graph.connections:
            zone1 = self.graph.zones[conn.zone1]
            zone2 = self.graph.zones[conn.zone2]
            self.ax.annotate('', xy=(zone2.x, zone2.y),
                             xytext=(zone1.x, zone1.y),
                             arrowprops=dict(arrowstyle='->', color='gray',
                             shrinkA=20, shrinkB=20))

        pos_x = [zone.x for zone in self.graph.zones.values()]
        pos_y = [zone.y for zone in self.graph.zones.values()]

        self.ax.set_xlim(min(pos_x) - 1, max(pos_x) + 1)
        self.ax.set_ylim(min(pos_y) - 1, max(pos_y) + 1)
        self.ax.set_aspect('equal')
