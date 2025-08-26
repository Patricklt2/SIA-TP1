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
from src.run_sokoban.sokoban import parse_map, SokobanState, precompute_dead_squares, get_neighbors

MAPS_DIR = Path("src/maps")
RESULTS_DIR = Path("src/results")
RESULTS_DIR.mkdir(exist_ok=True)

# Mapeo de nombres de heurísticas a funciones
HEURISTIC_MAP = {
    "manhattan": manhattan_heuristic,
    "boxes_out": heuristic_boxes_out,
    "player_boxes": player_boxes
}

def make_algo_map(sokoban_map, dead_squares, heuristic_name="manhattan"):
    """Crea el mapa de algoritmos con la heurística especificada"""
    heuristic_func = HEURISTIC_MAP[heuristic_name]
    
    return {
        "BFS": lambda s: bfs(s, sokoban_map.goals, sokoban_map, dead_squares, get_neighbors),
        "DFS": lambda s: dfs(s, sokoban_map.goals, sokoban_map, dead_squares, get_neighbors),
        "IDDFS": lambda s: iddfs(s, sokoban_map, dead_squares, get_neighbors, 1000),
        f"A_{heuristic_name}": lambda s: astar(s, sokoban_map, heuristic_func, dead_squares, get_neighbors),
        f"GGS_{heuristic_name}": lambda s: ggs(s, sokoban_map, heuristic_func, dead_squares, get_neighbors),
    }

def run_single_level(level_name):
    """Ejecuta todos los algoritmos en un solo nivel"""
    file_path = MAPS_DIR / f"{level_name}.txt"
    
    if not file_path.exists():
        print(f"❌ El archivo {file_path} no existe")
        return
    
    print(f"\n=== Ejecutando todos los algoritmos en {level_name} ===")
    results = []
    
    try:
        sokoban_map = parse_map(file_path)
        dead_squares = precompute_dead_squares(sokoban_map)
        initial_state = SokobanState(sokoban_map.player, sokoban_map.boxes)
        
        # Algoritmos sin heurística
        basic_algorithms = {
            "BFS": lambda s: bfs(s, sokoban_map.goals, sokoban_map, dead_squares, get_neighbors),
            "DFS": lambda s: dfs(s, sokoban_map.goals, sokoban_map, dead_squares, get_neighbors),
            "IDDFS": lambda s: iddfs(s, sokoban_map, dead_squares, get_neighbors, 1000),
        }
        
        # Ejecutar algoritmos básicos
        for algo_name, algo_func in basic_algorithms.items():
            print(f"Corriendo {algo_name} en {level_name}...")
            result = algo_func(initial_state)
            solution_list = result.get('solution', [])
            solution_str = ' '.join(f"{pos[0]},{pos[1]}" for pos, _id in solution_list) if solution_list else ''
            
            results.append({
                "level": level_name,
                "algorithm": algo_name,
                "heuristic": "N/A",
                "success": result['result'],
                "cost": result.get('cost'),
                "nodes_expanded": result.get('nodes_expanded'),
                "max_frontier": result.get('max_frontier'),
                "time": result.get('time'),
                "solution_length": len(result.get('solution', [])) if result.get('solution') else None,
                "solution": solution_str
            })
            print(f"✔ {algo_name} completado (success={result['result']})")
        
        # Ejecutar A* y GGS con diferentes heurísticas
        for heuristic_name in ["manhattan", "boxes_out", "player_boxes"]:
            heuristic_func = HEURISTIC_MAP[heuristic_name]
            
            # A* con heurística específica
            print(f"Corriendo A* con {heuristic_name} en {level_name}...")
            try:
                result_astar = astar(initial_state, sokoban_map, heuristic_func, dead_squares, get_neighbors)
                solution_list = result_astar.get('solution', [])
                solution_str = ' '.join(f"{pos[0]},{pos[1]}" for pos, _id in solution_list) if solution_list else ''
                
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
                    "solution": solution_str
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
            print(f"Corriendo GGS con {heuristic_name} en {level_name}...")
            try:
                result_ggs = ggs(initial_state, sokoban_map, heuristic_func, dead_squares, get_neighbors)
                solution_list = result_ggs.get('solution', [])
                solution_str = ' '.join(f"{pos[0]},{pos[1]}" for pos, _id in solution_list) if solution_list else ''
                
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
                    "solution": solution_str
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
        # Añadir entradas vacías para todos los algoritmos en caso de error
        algorithms = ["BFS", "DFS", "IDDFS"]
        for algo_name in algorithms:
            results.append({
                "level": level_name,
                "algorithm": algo_name,
                "heuristic": "N/A",
                "success": False,
                "cost": None,
                "nodes_expanded": None,
                "max_frontier": None,
                "time": None,
                "solution_length": None,
                "solution": ""
            })
        
        for heuristic_name in ["manhattan", "boxes_out", "player_boxes"]:
            for algo_name in ["A*", "GGS"]:
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
    out_file = RESULTS_DIR / f"{level_name}_results.csv"
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
    parser.add_argument("--all", action="store_true", help="Ejecutar en todos los niveles")
    
    args = parser.parse_args()
    
    if args.all:
        # Ejecutar en todos los niveles
        files = sorted(MAPS_DIR.glob("level_*.txt"))
        for file in files:
            level_name = file.stem
            run_single_level(level_name)
    else:
        # Ejecutar en el nivel específico
        run_single_level(args.level)

if __name__ == "__main__":
    main()