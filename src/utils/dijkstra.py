
from src.models import ZoneType, Graph, SpaceTimePath
from math import inf
import heapq

MAX_TURNS = 100
WAIT_TIE_BREAK = 0.01


def find_path(graph: Graph, start: str, end: str, res_zones:
              dict[tuple[str, int], int], res_conns:
              dict[tuple[str, str, int], int]) -> SpaceTimePath:
    """Find the fastest and most prioritized path in the Space-Time
                    Graph using Dijkstra."""

    if start == end:
        return [(start, 0)]

    def _is_zone_accessible(zone_name: str, turn: int) -> bool:
        """Check if the zone has available cap in a spec turn."""
        if zone_name in [start, end]:
            return True

        zone = graph.zones[zone_name]
        cur_occupants_turn = res_zones.get((zone_name, turn), 0)
        return cur_occupants_turn < zone.max_drones

    def _is_connection_accessible(from_zone: str,
                                  to_zone: str, turn: int) -> bool:
        """Check if the connection link has available cap in a spec turn."""

        conn = graph.get_connection(from_zone, to_zone)
        if not conn:
            return False

        cur_link_reservations = res_conns.get(
            (from_zone, to_zone, turn), 0)
        return cur_link_reservations < conn.max_link_capacity

    queue = [(0.0, 0, start, [(start, 0)])]
    best_weight = {(start, 0): 0.0}

    while queue:
        cur_weight, cur_turn, cur_zone, path = heapq.heappop(queue)

        if cur_turn > MAX_TURNS:
            break

        if cur_zone == end:
            return path

        if cur_weight > best_weight.get((cur_zone, cur_turn), inf):
            continue

        cur_zone_obj = graph.zones[cur_zone]
        wait_turn = cur_turn + 1
        wait_weight = cur_weight + cur_zone_obj.zone_weight() - WAIT_TIE_BREAK

        if _is_zone_accessible(cur_zone, wait_turn):
            if wait_weight < best_weight.get((cur_zone, wait_turn), inf):
                best_weight[(cur_zone, wait_turn)] = wait_weight
                heapq.heappush(queue, (wait_weight, wait_turn, cur_zone, path +
                               [(cur_zone, wait_turn)]))

        for neighbor in graph.get_neighbors(cur_zone):
            neighbor_zone = graph.zones[neighbor]
            neighbor_type = neighbor_zone.zone_type

            if neighbor_type == ZoneType.BLOCKED:
                continue

            if not _is_connection_accessible(cur_zone, neighbor, cur_turn):
                continue

            movement_cost = neighbor_zone.movement_cost()
            arrival_turn = cur_turn + movement_cost

            if neighbor_type == ZoneType.RESTRICTED:
                accessible = (_is_zone_accessible(neighbor, arrival_turn - 1)
                              and _is_zone_accessible(neighbor, arrival_turn))
            else:
                accessible = _is_zone_accessible(neighbor, arrival_turn)

            if accessible:
                zone_weight = neighbor_zone.zone_weight()
                new_weight = cur_weight + (movement_cost * zone_weight)

                if new_weight < best_weight.get((neighbor, arrival_turn), inf):
                    best_weight[(neighbor, arrival_turn)] = new_weight

                    if neighbor_type == ZoneType.RESTRICTED:
                        new_path = path + [(neighbor, arrival_turn - 1),
                                           (neighbor, arrival_turn)]
                    else:
                        new_path = path + [(neighbor, arrival_turn)]
                    heapq.heappush(queue, (new_weight, arrival_turn,
                                           neighbor, new_path))
    return []
