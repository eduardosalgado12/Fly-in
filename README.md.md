*This project has been created as part of the 42 curriculum by edsalgad.*

# Fly-in

## Description

Fly-in is a drone routing simulator. It reads a custom map file describing a
network of zones and connections, computes a collision-free, capacity-aware
path for every drone from the `start` zone to the `end` zone, and then runs
a turn-by-turn simulation printing the movement of every drone until all of
them have been delivered.

The project is fully object-oriented, statically typed (`mypy --strict`
clean), `flake8`-clean, and implements its own pathfinding algorithm without
relying on any external graph library.

Key features:
- Custom map parser, with strict validation of the input file format.
- A space-time Dijkstra pathfinding algorithm that reserves zones and
  connections turn by turn, so multiple drones can be routed without
  colliding or exceeding capacity.
- Support for `normal`, `restricted`, `priority` and `blocked` zone types,
  each with their own movement cost/behaviour.
- A graphical visual representation of the simulation (built with
  `matplotlib`), showing zones, connections and drones animated turn by
  turn.

## Instructions

### Requirements

- Python 3.10 or later.
- A virtual environment is recommended (see `python3 -m venv venv`).

### Installation

```bash
make install
```

This installs the project's dependencies (currently only `matplotlib`,
listed in `requirements.txt`) using `pip`.

### Running the simulation

```bash
make run MAP=<path-to-map-file>
```

For example:

```bash
make run MAP=maps/easy/01_linear_path.txt
```

If `MAP` is omitted, it defaults to `maps/easy/01_linear_path.txt`.

You can also run it directly with Python:

```bash
python3 main.py <path-to-map-file>
```

### Debugging

```bash
make debug MAP=<path-to-map-file>
```

Runs the simulation inside Python's built-in debugger (`pdb`).

### Linting

```bash
make lint         # flake8 + mypy (mandatory flags)
make lint-strict   # flake8 + mypy --strict
```

### Cleaning

```bash
make clean
```

Removes `__pycache__` directories and the `.mypy_cache`.

## Algorithm and Implementation Strategy

### Modeling the problem as a space-time graph

Each drone needs a path that never puts it in the same zone, at the same
turn, as too many other drones (respecting `max_drones`), and never uses a
connection, at the same turn, beyond its `max_link_capacity`. Instead of
searching only over zones, the pathfinder (`src/utils/dijkstra.py`) searches
over **(zone, turn) pairs** — a "space-time graph". Two states `(zoneA, t)`
and `(zoneB, t')` are connected if a drone can legally move from `zoneA` to
`zoneB` between turn `t` and turn `t'`, given the zone's movement cost and
type.

Each drone's path is computed **sequentially**, one drone at a time, with a
classic Dijkstra search over this space-time graph. After a drone's path is
found, every `(zone, turn)` and `(zone1, zone2, turn)` it occupies is
"reserved" in two dictionaries (`reservation_zones`,
`reservation_connections`). The next drone's search takes these reservations
into account, so it is automatically routed around zones/connections that
are already full at that turn — this is what allows multiple drones to be
scheduled without conflicts, without needing a full multi-agent search.

Movement costs and priorities:
- `normal`: 1 turn to enter.
- `restricted`: 2 turns to enter; the drone occupies the connection during
  transit and must arrive on the next turn (no waiting on the connection).
- `priority`: 1 turn to enter, but weighted slightly cheaper
  (`zone_weight`) so the search prefers it when a tie exists.
- `blocked`: never enters the search space at all.

To avoid the search exploring forever when no path exists (e.g. the only
route is behind a `blocked` zone), the search is capped at `MAX_TURNS`.
A small tie-breaking weight (`WAIT_TIE_BREAK`) makes "wait in place"
strictly cheaper than a pointless detour when both would otherwise cost the
same, avoiding dead-end wandering.

### Complexity

For a single drone, the search space has at most `V * MAX_TURNS` distinct
`(zone, turn)` states, where `V` is the number of zones. Each state has a
bounded number of outgoing edges (its neighbours in the zone graph, plus the
"wait" edge), so the search behaves like a standard Dijkstra over a graph
with `O(V * MAX_TURNS)` nodes and `O(E * MAX_TURNS)` edges (`E` being the
number of connections):

- Time: `O(E * MAX_TURNS * log(V * MAX_TURNS))` per drone (binary heap).
- Space: `O(V * MAX_TURNS)` per drone, for the `best_weight` map and the
  priority queue.

For `D` drones, the total pathfinding cost is `O(D * E * MAX_TURNS *
log(V * MAX_TURNS))`, since paths are computed sequentially and each
drone's search is independent of the others (only reading/writing the
shared reservation dictionaries, which are `O(1)` lookups/updates).

Paths are **not** recalculated once found — each drone's path is computed
once, stored on the `Drone` instance, and simply replayed turn by turn
during `Simulation.run()`, which is an `O(D)` operation per turn.

## Visual Representation

`src/core/visualizer.py` implements a graphical visual representation using
`matplotlib`:

- `draw_map()` draws every zone as a coloured circle (using the zone's
  `color` metadata, or a default colour), sized to reflect its `max_drones`
  capacity, and every connection as an arrow between zones. Zone names are
  labeled below each circle.
- `update_drones()` is called once per simulation turn and redraws the
  drones at their current position. Drones sharing the same zone are spread
  out in a small circle around the zone's center, each labeled with its id,
  so they never overlap. The current turn number is shown as the plot's
  title.

This gives a live, animated view of the whole simulation as it runs,
instead of only the raw text output — making it easy to see, at a glance,
how drones are being distributed across the network, where bottlenecks
happen (zones/connections at capacity), and how `restricted` zones and
waiting affect the overall routing.

## Example

Given `maps/easy/01_linear_path.txt`:

```
# Easy Level 1: Simple linear path
nb_drones: 2

start_hub: start 0 0 [color=green]
hub: waypoint1 1 0 [color=blue]
hub: waypoint2 2 0 [color=blue]
end_hub: goal 3 0 [color=red]

connection: start-waypoint1
connection: waypoint1-waypoint2
connection: waypoint2-goal
```

Running `make run MAP=maps/easy/01_linear_path.txt` produces:

```
D1-waypoint1
D1-waypoint2 D2-waypoint1
D1-goal D2-waypoint2
D2-goal
```

(4 turns — within the target of `<= 6` turns for this map.)

## Resources

### Documentation and references

- [Dijkstra's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Python `heapq` documentation](https://docs.python.org/3/library/heapq.html)
- [Python `typing` documentation](https://docs.python.org/3/library/typing.html)
- [mypy documentation](https://mypy.readthedocs.io/)
- [flake8 documentation](https://flake8.pycqa.org/)
- [matplotlib documentation](https://matplotlib.org/stable/index.html)

### AI usage disclosure

AI assistance (Claude) was used as a learning and review tool throughout
this project, with every suggestion reviewed and understood before being
kept:
- Helping debug the pathfinder (`src/utils/dijkstra.py`), for example
  spotting an infinite loop when a `blocked` zone cuts off the only path to
  the goal.
- Explaining `matplotlib` concepts used in `src/core/visualizer.py`
  (figures/axes, patches, redraw-based animation), applied while writing
  the code.
- Pointing out `mypy`/`flake8` issues and suggesting fixes, and reviewing
  code structure (constants, type aliases, removing dead code).
