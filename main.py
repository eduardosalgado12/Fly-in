
import sys

from parser import Parser, ParserError

if __name__ == "__main__":

    file = sys.argv[1]

    p = Parser()

    try:
        p.parse(file)
    except ParserError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print("Zonas no grafo:", list(p.graph.zones.keys()))
    print("Conexoes:", p.graph.connections)
    print("Numeros de drones", p.nb_drones)
    print("Vizinhos de 'hub':", p.graph.get_neighbors("start"))
    print("Custo de mover para 'junction' (restricted):",
          p.graph.zones["junction"].movement_cost())
