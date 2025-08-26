import os
import csv
import time
from pathlib import Path
from src.run_sokoban.sokoban import parse_map, SokobanState, precompute_dead_squares, get_neighbors
from src.run_sokoban.search_algorithms.bfs import bfs
from src.run_sokoban.search_algorithms.dfs import dfs
from src.run_sokoban.search_algorithms.iddfs import iddfs
from src.run_sokoban.search_algorithms.astar import astar
from src.run_sokoban.search_algorithms.ggs import ggs
from src.run_sokoban.search_algorithms.heuristics import manhattan_heuristic, heuristic_boxes_out, player_boxes

MAPS_DIR = Path("src/maps2")
RESULTS_DIR = Path("src/results")
RESULTS_DIR.mkdir(exist_ok=True)
OUTPUT_FILE = RESULTS_DIR / "consolidated_results_all.csv"

def run_algorithm(algo_name, initial_state, sokoban_map, dead_squares, heuristic=None):
    algorithms = {
        # Uninformed algorithms - don't use heuristic parameter
        "BFS": lambda s: bfs(s, sokoban_map.goals, sokoban_map, dead_squares, get_neighbors),
        "DFS": lambda s: dfs(s, sokoban_map.goals, sokoban_map, dead_squares, get_neighbors),
        "IDDFS": lambda s: iddfs(s, sokoban_map, dead_squares, get_neighbors, 1000),
        # Informed algorithms - use heuristic parameter
        "A*": lambda s: astar(s, sokoban_map, heuristic, dead_squares, get_neighbors),
        "GGS": lambda s: ggs(s, sokoban_map, heuristic, dead_squares, get_neighbors)
    }

    # Get heuristic name for display
    if algo_name in ["BFS", "DFS", "IDDFS"]:
        heuristic_name = "N/A"
    else:
        heuristic_display_names = {
            'manhattan_heuristic': 'manhattan',
            'heuristic_boxes_out': 'boxes_out',
            'player_boxes': 'player_boxes'
        }
        heuristic_name = heuristic_display_names.get(heuristic.__name__, "N/A")

    # Measure execution time more accurately
    start_time = time.perf_counter()  # Use perf_counter for higher precision
    result = algorithms[algo_name](initial_state)
    end_time = time.perf_counter()
    
    # Add execution time to result
    result['time'] = max(end_time - start_time, 0.000001)  # Ensure minimum resolution of 1 microsecond
    
    return result, heuristic_name

def run_all_levels():
    # Get all level files sorted numerically
    level_files = sorted(
        MAPS_DIR.glob("level_*.txt"),
        key=lambda x: int(x.stem.split('_')[1])
    )
    
    algorithms = ["BFS", "DFS", "IDDFS"]
    informed_algorithms = {
        "A*": [manhattan_heuristic, heuristic_boxes_out, player_boxes],
        "GGS": [manhattan_heuristic, heuristic_boxes_out, player_boxes]
    }

    # Write header
    with open(OUTPUT_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["level", "algorithm", "heuristic", "success", "cost", 
                        "nodes_expanded", "max_frontier", "time", "solution_length"])

    for file in level_files:
        level_name = file.stem
        print(f"\nProcessing {level_name}...")
        
        try:
            sokoban_map = parse_map(file)
            dead_squares = precompute_dead_squares(sokoban_map)
            initial_state = SokobanState(sokoban_map.player, sokoban_map.boxes)

            # Run uninformed algorithms
            for algo_name in algorithms:
                print(f"Running {algo_name}...")
                try:
                    result, heuristic_name = run_algorithm(algo_name, initial_state, sokoban_map, dead_squares)
                    with open(OUTPUT_FILE, 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            level_name,
                            algo_name,
                            heuristic_name,
                            result["result"],
                            result.get("cost"),
                            result.get("nodes_expanded"),
                            result.get("max_frontier"),
                            result.get("time"),
                            len(result.get("solution", [])) if result.get("solution") else None
                        ])
                    print(f"Results written for {level_name} - {algo_name}")
                except Exception as e:
                    print(f"Error running {algo_name}: {str(e)}")
                    with open(OUTPUT_FILE, 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([level_name, algo_name, "N/A", f"Error: {str(e)}", 
                                       None, None, None, None, None])

            # Run informed algorithms with different heuristics
            for algo_name, heuristics in informed_algorithms.items():
                for heuristic in heuristics:
                    print(f"Running {algo_name} with {heuristic.__name__}...")
                    try:
                        result, heuristic_name = run_algorithm(algo_name, initial_state, sokoban_map, dead_squares, heuristic)
                        with open(OUTPUT_FILE, 'a', newline='') as f:
                            writer = csv.writer(f)
                            writer.writerow([
                                level_name,
                                algo_name,
                                heuristic_name,
                                result["result"],
                                result.get("cost"),
                                result.get("nodes_expanded"),
                                result.get("max_frontier"),
                                result.get("time"),
                                len(result.get("solution", [])) if result.get("solution") else None
                            ])
                        print(f"Results written for {level_name} - {algo_name} - {heuristic_name}")
                    except Exception as e:
                        print(f"Error running {algo_name} with {heuristic.__name__}: {str(e)}")
                        with open(OUTPUT_FILE, 'a', newline='') as f:
                            writer = csv.writer(f)
                            writer.writerow([level_name, algo_name, heuristic.__name__, f"Error: {str(e)}", 
                                           None, None, None, None, None])

        except Exception as e:
            print(f"Error processing {level_name}: {str(e)}")
            continue

    print(f"\nAll results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    run_all_levels()