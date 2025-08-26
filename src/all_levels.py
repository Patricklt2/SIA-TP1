import os
import csv
from pathlib import Path

from src.run_sokoban.search_algorithms.bfs import bfs
from src.run_sokoban.search_algorithms.dfs import dfs
from src.run_sokoban.search_algorithms.iddfs import iddfs
from src.run_sokoban.search_algorithms.astar import astar
from src.run_sokoban.search_algorithms.ggs import ggs
from src.run_sokoban.search_algorithms.heuristics import manhattan_heuristic
from src.run_sokoban.sokoban import parse_map, SokobanState, precompute_dead_squares, get_neighbors

MAPS_DIR = Path("src/maps2")
RESULTS_DIR = Path("src/results")
RESULTS_DIR.mkdir(exist_ok=True)

# Definimos los algoritmos (usamos manhattan como heurística default)
def make_algo_map(sokoban_map, dead_squares):
    return {
        "BFS": lambda s: bfs(s, sokoban_map.goals, sokoban_map, dead_squares, get_neighbors),
        "DFS": lambda s: dfs(s, sokoban_map.goals, sokoban_map, dead_squares, get_neighbors),
        "IDDFS": lambda s: iddfs(s, sokoban_map, dead_squares, get_neighbors, 1000),
        "A": lambda s: astar(s, sokoban_map, manhattan_heuristic, dead_squares, get_neighbors),
        "GGS": lambda s: ggs(s, sokoban_map, manhattan_heuristic, dead_squares, get_neighbors),
    }

def run_all_levels():
    files = sorted(MAPS_DIR.glob("level_*.txt"))

    for algo_name in ["BFS", "DFS", "IDDFS", "A", "GGS"]:
        print(f"\n=== Ejecutando {algo_name} en todos los niveles ===")
        results = []

        for idx, file in enumerate(files, start=1):
            level_name = file.stem
            print(f"[{idx}] Corriendo {algo_name} en {level_name}...")

            try:
                sokoban_map = parse_map(file)
                dead_squares = precompute_dead_squares(sokoban_map)
                initial_state = SokobanState(sokoban_map.player, sokoban_map.boxes)

                algo_map = make_algo_map(sokoban_map, dead_squares)
                result = algo_map[algo_name](initial_state)

                results.append({
                    "level": level_name,
                    "success": result['result'],
                    "cost": result.get('cost'),
                    "nodes_expanded": result.get('nodes_expanded'),
                    "max_frontier": result.get('max_frontier'),
                    "time": result.get('time'),
                    "solution_length": len(result.get('solution', [])) if result.get('solution') else None
                })

                print(f"✔ {level_name} completado (success={result['result']})")

            except Exception as e:
                print(f"❌ Error en {level_name}: {e}")
                results.append({
                    "level": level_name,
                    "success": False,
                    "cost": None,
                    "nodes_expanded": None,
                    "max_frontier": None,
                    "time": None,
                    "solution_length": None,
                })

        # Guardar CSV específico de este algoritmo
        out_file = RESULTS_DIR / f"{algo_name.lower()}_results.csv"
        with open(out_file, "w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["level", "success", "cost", "nodes_expanded", "max_frontier", "time", "solution_length"]
            )
            writer.writeheader()
            writer.writerows(results)

        print(f"✅ Resultados de {algo_name} guardados en {out_file}")

if __name__ == "__main__":
    run_all_levels()
