import os 
from src.run_sokoban.sokoban import parse_map, SokobanState
from src.run_sokoban.search_algorithms.bfs import bfs
from src.run_sokoban.search_algorithms.dfs import dfs
from src.run_sokoban.search_algorithms.iddfs import iddfs
from src.run_sokoban.search_algorithms.astar import astar
from src.run_sokoban.search_algorithms.ggs import ggs
from src.run_sokoban.search_algorithms.heuristics import manhattan_heuristic, heuristic_boxes_out

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    map_file = os.path.join(BASE_DIR, "maps", "level2.txt")
    sokoban_map = parse_map(map_file)

    initial_state = SokobanState(sokoban_map.player, sokoban_map.boxes)
    result = bfs(initial_state, sokoban_map.goals, sokoban_map)
    result2 = dfs(initial_state, sokoban_map.goals, sokoban_map)
    result3 = iddfs(initial_state, sokoban_map, 50)
    result4 = astar(initial_state, sokoban_map, manhattan_heuristic)
    result5 = ggs(initial_state, sokoban_map, manhattan_heuristic)

    print(f"Resultado: {result['result']}")
    print(f"Costo de la solución: {result['cost']}")
    print(f"Nodos expandidos: {result['nodes_expanded']}")
    print(f"Tamaño máximo de la frontera: {result['max_frontier']}")
    print(f"Tiempo de procesamiento: {result['time']:.4f} s")
    print(f"Solución (movimientos): {result['solution']}")

    print(f"Resultado: {result2['result']}")
    print(f"Costo de la solución: {result2['cost']}")
    print(f"Nodos expandidos: {result2['nodes_expanded']}")
    print(f"Tamaño máximo de la frontera: {result2['max_frontier']}")
    print(f"Tiempo de procesamiento: {result2['time']:.4f} s")
    print(f"Solución (movimientos): {result2['solution']}")

    print(f"Resultado: {result3['result']}")
    print(f"Costo de la solución: {result3['cost']}")
    print(f"Nodos expandidos: {result3['nodes_expanded']}")
    print(f"Tamaño máximo de la frontera: {result3['max_frontier']}")
    print(f"Tiempo de procesamiento: {result3['time']:.4f} s")
    print(f"Solución (movimientos): {result3['solution']}")

    print(f"Resultado: {result4['result']}")
    print(f"Costo de la solución: {result4['cost']}")
    print(f"Nodos expandidos: {result4['nodes_expanded']}")
    print(f"Tamaño máximo de la frontera: {result4['max_frontier']}")
    print(f"Tiempo de procesamiento: {result4['time']:.4f} s")
    print(f"Solución (movimientos): {result4['solution']}")

    print(f"Resultado: {result5['result']}")
    print(f"Costo de la solución: {result5['cost']}")
    print(f"Nodos expandidos: {result5['nodes_expanded']}")
    print(f"Tamaño máximo de la frontera: {result5['max_frontier']}")
    print(f"Tiempo de procesamiento: {result5['time']:.4f} s")
    print(f"Solución (movimientos): {result5['solution']}")