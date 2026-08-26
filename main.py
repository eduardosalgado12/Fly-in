
import sys
from parser import Parser
from simulation import Simulation

if __name__ == "__main__":

    file = sys.argv[1]
    parser = Parser()
    parser.parse(file)

    sim = Simulation(parser.nb_drones, parser.graph)
    sim.run()
