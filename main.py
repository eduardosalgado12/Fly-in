
import sys
from src.parser import Parser
from src.simulation import Simulation

if __name__ == "__main__":

    file = sys.argv[1]
    parser = Parser()
    parser.parse(file)

    sim = Simulation(parser.nb_drones, parser.graph)
    sim.run()
