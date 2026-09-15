
import sys
from src.utils import Parser
from src.core.simulation import Simulation


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
    except Exception as e:
        print(f"Parsing Error: {e}")
        sys.exit(1)

    sim = Simulation(parser.nb_drones, parser.graph)
    sim.run()


if __name__ == "__main__":
    main()
