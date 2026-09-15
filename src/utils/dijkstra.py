
from src.models import ZoneType, Zone, Graph
import heapq


def find_path(graph: Graph, start: str, end: str, res_zones: dict,
              res_conns: dict) -> list[tuple[str, int]]:
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
    best_weights = {(start, 0): 0.0}

    while queue:
        cur_weight, cur_turn, cur_zone, path = heapq.heappop(queue)

        if cur_zone == end:
            return path

        if cur_turn > best_weights.get((cur_zone, cur_turn), float('inf')):
            continue

        wait_turn = cur_turn + 1
        if _is_zone_accessible(cur_zone, wait_turn):
            if wait_turn < best_turns.get(
              (current_zone, wait_turn), float('inf')):
                best_turns[(current_zone, wait_turn)] = wait_turn
                heapq.heappush(queue, (wait_turn, current_zone, path +
                               [(current_zone, wait_turn)]))

        for neighbor in graph.get_neighbors(current_zone):
            neighbor_zone = graph.zones[neighbor]
            neighbor_type = neighbor_zone.zone_type

            if neighbor_type == ZoneType.BLOCKED:
                continue

            arrival_turn = current_turn + Zone.movement_cost(neighbor_zone)

            if not _is_connection_accessible(
                 current_zone, neighbor, current_turn):
                continue

            if neighbor_type == ZoneType.RESTRICTED:
                accessible = (_is_zone_accessible(
                    neighbor, arrival_turn - 1) and
                    _is_zone_accessible(neighbor, arrival_turn))
            else:
                accessible = _is_zone_accessible(
                     neighbor, arrival_turn)

            if accessible:
                if arrival_turn < best_turns.get(
                     (neighbor, arrival_turn), float('inf')):
                    best_turns[(neighbor, arrival_turn)] = arrival_turn

                    if neighbor_type == ZoneType.RESTRICTED:
                        new_path = path + [
                            (neighbor, arrival_turn - 1),
                            (neighbor, arrival_turn)]
                    else:
                        new_path = path + [(neighbor, arrival_turn)]

                    heapq.heappush(queue, (arrival_turn, neighbor, new_path))

    return []
