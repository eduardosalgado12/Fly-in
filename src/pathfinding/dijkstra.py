
import heapq


def find_path(self, start: str, end: str) -> list[tuple[str, int]]:
        """Find the fastest path in the Space-Time Graph using Dijkstra."""

        if start == end:
            return [(start, 0)]

        queue = [(0, start, [(start, 0)])]
        best_turns = {(start, 0): 0}

        while queue:
            current_turn, current_zone, path = heapq.heappop(queue)

            if current_zone == end:
                return path

            if current_turn > best_turns.get((current_zone, current_turn), float('inf')):
                continue

            wait_turn = current_turn + 1
            if self._is_zone_accessible(current_zone, wait_turn):
                if wait_turn < best_turns.get((current_zone, wait_turn), float('inf')):
                    best_turns[(current_zone, wait_turn)] = wait_turn
                    heapq.heappush(queue, (wait_turn, current_zone, path + [(current_zone, wait_turn)]))

            for neighbor in self.graph.get_neighbors(current_zone):
                visited = {p_zone for p_zone, p_turn in path}
                if neighbor in visited:
                    continue

                neighbor_zone = self.graph.zones[neighbor]
                neighbor_type = neighbor_zone.zone_type

                if neighbor_type == ZoneType.BLOCKED:
                    continue

                arrival_turn = current_turn + Zone.movement_cost(neighbor_zone)

                if not self._is_connection_accessible(current_zone, neighbor, arrival_turn):
                    continue

                if neighbor_type == ZoneType.RESTRICTED:
                    accessible = (self._is_zone_accessible(neighbor, arrival_turn - 1) and
                                  self._is_zone_accessible(neighbor, arrival_turn))
                else:
                    accessible = self._is_zone_accessible(neighbor, arrival_turn)

                if accessible:
                    if arrival_turn < best_turns.get((neighbor, arrival_turn), float('inf')):
                        best_turns[(neighbor, arrival_turn)] = arrival_turn

                        if neighbor_type == ZoneType.RESTRICTED:
                            new_path = path + [(neighbor, arrival_turn - 1), (neighbor, arrival_turn)]
                        else:
                            new_path = path + [(neighbor, arrival_turn)]

                        heapq.heappush(queue, (arrival_turn, neighbor, new_path))
        print(queue)

        return []


def _is_zone_accessible(self, zone_name: str, turn: int) -> bool:
    """Check if the zone has available capacity in a specific turn."""
    if zone_name in [self.start, self.end]:
        return True

    zone = self.graph.zones[zone_name]
    cur_occupants_turn = self.reservation_zones.get((zone_name, turn), 0)
    return cur_occupants_turn < zone.max_drones

def _is_connection_accessible(self, from_zone: str, to_zone: str, turn: int) -> bool:
    """Check if the connection link has available capacity in a specific turn."""
    conn = self.graph.get_connection(from_zone, to_zone)
    if not conn:
        return False

    cur_link_reservations = self.reservation_connections.get((from_zone, to_zone, turn), 0)
    return cur_link_reservations < conn.max_link_capacity
