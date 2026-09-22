
from src.models import ZoneType, Graph, SpaceTimePath
from math import inf
import heapq

MAX_TURNS = 100
WAIT_TIE_BREAK = 0.01


def find_path(graph: Graph, start: str, end: str, res_zones:
              dict[tuple[str, int], int], res_conns:
              dict[tuple[str, str, int], int]) -> SpaceTimePath:
    """Finds the fastest and most prioritized path in the space-time graph.

    Searches over (zone, turn) states with Dijkstra's algorithm, so the
    resulting path already accounts for other drones' reservations
    (`res_zones`/`res_conns`) and never revisits a zone/connection at a
    turn where it would exceed capacity.

    Args:
        graph: The zone graph to search.
        start: Name of the zone to start from.
        end: Name of the destination zone.
        res_zones: Mapping of `(zone_name, turn)` to the number of drones
            already reserved there, used to avoid capacity conflicts.
        res_conns: Mapping of `(from_zone, to_zone, turn)` to the number of
            drones already reserved on that connection at that turn.

    Returns:
        The path as a list of `(zone_name, turn)` pairs, from `start` at
        turn 0 to `end`. A `RESTRICTED` zone contributes two entries (its
        departure and arrival turns). Returns an empty list if no path is
        found within `MAX_TURNS`.
    """
    if start == end:
        return [(start, 0)]

    def _is_zone_accessible(zone_name: str, turn: int) -> bool:
        """Checks if the zone has available capacity at a specific turn.

        Args:
            zone_name: Name of the zone to check.
            turn: The turn at which to check availability.

        Returns:
            True if `start`/`end` (unlimited capacity), or if the zone has
            not yet reached `max_drones` reservations at that turn.
        """
        if zone_name in [start, end]:
            return True

        zone = graph.zones[zone_name]
        cur_occupants_turn = res_zones.get((zone_name, turn), 0)
        return cur_occupants_turn < zone.max_drones

    def _is_connection_accessible(from_zone: str,
                                  to_zone: str, turn: int) -> bool:
        """Checks if the connection has available capacity at a turn.

        Args:
            from_zone: Name of the zone the connection departs from.
            to_zone: Name of the zone the connection arrives at.
            turn: The turn at which to check availability.

        Returns:
            True if the connection exists and has not yet reached
            `max_link_capacity` reservations at that turn.
        """
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
