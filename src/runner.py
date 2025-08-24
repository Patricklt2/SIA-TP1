import os 
from sokoban import parse_map, SokobanState
from bfs import bfs

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    map_file = os.path.join(BASE_DIR, "maps", "level2.txt")
    sokoban_map = parse_map(map_file)

    initial_state = SokobanState(sokoban_map.player, sokoban_map.boxes)
    result = bfs(initial_state, sokoban_map.goals, sokoban_map)

    print(f"Resultado: {result['result']}")
    print(f"Costo de la solución: {result['cost']}")
    print(f"Nodos expandidos: {result['nodes_expanded']}")
    print(f"Tamaño máximo de la frontera: {result['max_frontier']}")
    print(f"Tiempo de procesamiento: {result['time']:.4f} s")
    print(f"Solución (movimientos): {result['solution']}")