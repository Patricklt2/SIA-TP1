import os
import csv
import argparse
from pathlib import Path

from src.run_sokoban.search_algorithms.bfs import bfs
from src.run_sokoban.search_algorithms.dfs import dfs
from src.run_sokoban.search_algorithms.iddfs import iddfs
from src.run_sokoban.search_algorithms.astar import astar
from src.run_sokoban.search_algorithms.ggs import ggs
from src.run_sokoban.search_algorithms.heuristics import manhattan_heuristic, heuristic_boxes_out, player_boxes
from src.run_sokoban.sokoban import parse_map, SokobanState, precompute_dead_squares, get_neighbors, get_push_neighbors

MAPS_DIR = Path("src/maps")
RESULTS_DIR = Path("src/results")
RESULTS_DIR.mkdir(exist_ok=True)

# Mapeo de nombres de heurísticas a funciones
HEURISTIC_MAP = {
    "manhattan": manhattan_heuristic,
    "boxes_out": heuristic_boxes_out,
    "player_boxes": player_boxes
}

MODE_MAP = {
    "player": get_neighbors,
    "push": get_push_neighbors
}

# Mapeo de algoritmos disponibles
ALGORITHM_MAP = {
    "bfs": bfs,
    "dfs": dfs, 
    "iddfs": iddfs,
    "astar": astar,
    "ggs": ggs
}

def run_single_level(level_name, mode, algorithms_to_run=None):
    """Ejecuta algoritmos específicos en un solo nivel"""
    file_path = MAPS_DIR / f"{level_name}.txt"
    
    if not file_path.exists():
        print(f"❌ El archivo {file_path} no existe")
        return
    
    print(f"\n=== Ejecutando algoritmos en {level_name} (modo: {mode}) ===")
    results = []
    
    try:
        sokoban_map = parse_map(file_path)
        dead_squares = precompute_dead_squares(sokoban_map)
        initial_state = SokobanState(sokoban_map.player, sokoban_map.boxes)
        
        # Si no se especifican algoritmos, ejecutar todos
        if algorithms_to_run is None:
            algorithms_to_run = ["bfs", "dfs", "iddfs", "astar", "ggs"]
        
        # Ejecutar algoritmos básicos (sin heurística)
        basic_algorithms = {
            "bfs": lambda s: bfs(s, sokoban_map.goals, sokoban_map, dead_squares, MODE_MAP[mode]),
            "dfs": lambda s: dfs(s, sokoban_map.goals, sokoban_map, dead_squares, MODE_MAP[mode]),
            "iddfs": lambda s: iddfs(s, sokoban_map, dead_squares, MODE_MAP[mode], 1000),
        }
        
        # Ejecutar algoritmos básicos seleccionados
        for algo_name in algorithms_to_run:
            if algo_name in basic_algorithms:
                print(f"Corriendo {algo_name.upper()} en {level_name}...")
                result = basic_algorithms[algo_name](initial_state)
                
                results.append({
                    "level": level_name,
                    "algorithm": algo_name.upper(),
                    "heuristic": "N/A",
                    "success": result['result'],
                    "cost": result.get('cost'),
                    "nodes_expanded": result.get('nodes_expanded'),
                    "max_frontier": result.get('max_frontier'),
                    "time": result.get('time'),
                    "solution_length": len(result.get('solution', [])) if result.get('solution') else None,
                    "solution": result.get('solution')
                })
                print(f"✔ {algo_name.upper()} completado (success={result['result']})")
        
        # Ejecutar A* y GGS con diferentes heurísticas (si están seleccionados)
        if "astar" in algorithms_to_run or "ggs" in algorithms_to_run:
            for heuristic_name in ["manhattan", "boxes_out", "player_boxes"]:
                heuristic_func = HEURISTIC_MAP[heuristic_name]
                
                # A* con heurística específica
                if "astar" in algorithms_to_run:
                    print(f"Corriendo A* con {heuristic_name} en {level_name}...")
                    try:
                        result_astar = astar(initial_state, sokoban_map, heuristic_func, dead_squares, MODE_MAP[mode])
                        
                        results.append({
                            "level": level_name,
                            "algorithm": "A*",
                            "heuristic": heuristic_name,
                            "success": result_astar['result'],
                            "cost": result_astar.get('cost'),
                            "nodes_expanded": result_astar.get('nodes_expanded'),
                            "max_frontier": result_astar.get('max_frontier'),
                            "time": result_astar.get('time'),
                            "solution_length": len(result_astar.get('solution', [])) if result_astar.get('solution') else None,
                            "solution": result_astar.get('solution'),
                        })
                        print(f"✔ A*_{heuristic_name} completado (success={result_astar['result']})")
                    except Exception as e:
                        print(f"❌ Error en A*_{heuristic_name}: {e}")
                        results.append({
                            "level": level_name,
                            "algorithm": "A*",
                            "heuristic": heuristic_name,
                            "success": False,
                            "cost": None,
                            "nodes_expanded": None,
                            "max_frontier": None,
                            "time": None,
                            "solution_length": None,
                            "solution": ""
                        })
                
                # GGS con heurística específica
                if "ggs" in algorithms_to_run:
                    print(f"Corriendo GGS con {heuristic_name} en {level_name}...")
                    try:
                        result_ggs = ggs(initial_state, sokoban_map, heuristic_func, dead_squares, MODE_MAP[mode])
                        
                        results.append({
                            "level": level_name,
                            "algorithm": "GGS",
                            "heuristic": heuristic_name,
                            "success": result_ggs['result'],
                            "cost": result_ggs.get('cost'),
                            "nodes_expanded": result_ggs.get('nodes_expanded'),
                            "max_frontier": result_ggs.get('max_frontier'),
                            "time": result_ggs.get('time'),
                            "solution_length": len(result_ggs.get('solution', [])) if result_ggs.get('solution') else None,
                            "solution": result_ggs.get('solution'),
                        })
                        print(f"✔ GGS_{heuristic_name} completado (success={result_ggs['result']})")
                    except Exception as e:
                        print(f"❌ Error en GGS_{heuristic_name}: {e}")
                        results.append({
                            "level": level_name,
                            "algorithm": "GGS",
                            "heuristic": heuristic_name,
                            "success": False,
                            "cost": None,
                            "nodes_expanded": None,
                            "max_frontier": None,
                            "time": None,
                            "solution_length": None,
                            "solution": ""
                        })
                
    except Exception as e:
        print(f"❌ Error general en {level_name}: {e}")
        # Añadir entradas vacías para los algoritmos seleccionados
        for algo_name in algorithms_to_run:
            if algo_name in ["bfs", "dfs", "iddfs"]:
                results.append({
                    "level": level_name,
                    "algorithm": algo_name.upper(),
                    "heuristic": "N/A",
                    "success": False,
                    "cost": None,
                    "nodes_expanded": None,
                    "max_frontier": None,
                    "time": None,
                    "solution_length": None,
                    "solution": ""
                })
        
        if "astar" in algorithms_to_run or "ggs" in algorithms_to_run:
            for heuristic_name in ["manhattan", "boxes_out", "player_boxes"]:
                for algo_name in ["A*", "GGS"]:
                    if (algo_name == "A*" and "astar" in algorithms_to_run) or (algo_name == "GGS" and "ggs" in algorithms_to_run):
                        results.append({
                            "level": level_name,
                            "algorithm": algo_name,
                            "heuristic": heuristic_name,
                            "success": False,
                            "cost": None,
                            "nodes_expanded": None,
                            "max_frontier": None,
                            "time": None,
                            "solution_length": None,
                            "solution": ""
                        })

    # Guardar CSV para este nivel
    out_file = RESULTS_DIR / f"{level_name}_{mode}_results.csv"
    with open(out_file, "w", newline="", encoding='utf-8') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "level", "algorithm", "heuristic", "success", "cost", 
                "nodes_expanded", "max_frontier", "time", "solution_length", "solution"
            ]
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"✅ Resultados de {level_name} guardados en {out_file}")
    
    return results

def main():
    """Función principal con argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(description="Ejecutar algoritmos de Sokoban en un nivel específico")
    parser.add_argument("level", help="Nombre del nivel (ej: level_1, level_2)")
    parser.add_argument("mode", choices=["player", "push"], help="Modo de ejecución: player o push")
    parser.add_argument("--algorithms", "-a", nargs="+", choices=["bfs", "dfs", "iddfs", "astar", "ggs"],
                       help="Algoritmos específicos a ejecutar (por defecto: todos)")
    
    args = parser.parse_args()
    run_single_level(args.level, args.mode, args.algorithms)

if __name__ == "__main__":
    main()