import sys
from src.utils import Parser, ParserError
from src.core import Simulation, Visualizer


def main() -> None:
    """Main execution entry point for the Fly-in drone simulation."""

    if len(sys.argv) < 2:
        print("Error: Please provide a map file path.")
        print("Usage: python3 main.py <map_path>")
        sys.exit(1)

    file = sys.argv[1]
    parser = Parser()
    try:
        parser.parse(file)
    except ParserError as e:
        print(f"Parsing Error: {e}")
        sys.exit(1)

    v = Visualizer(parser.graph)
    v.draw_map()

    try:
        sim = Simulation(parser.nb_drones, parser.graph, v)
        sim.run()
    except ValueError as e:
        print(f"Simulation Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
