import time
import heapq
import itertools
from ..sokoban import reconstruct_path, get_neighbors

def ggs(initial_state, sokoban_map, heuristic):
    start_time = time.time()
    goals = sokoban_map.goals
    frontier = []
    counter = itertools.count()

    heapq.heappush(frontier, (heuristic(initial_state, goals), next(counter), initial_state))
    explored = set()
    max_frontier = 1
    nodes_expanded = 0

    while frontier:
        _, _, state = heapq.heappop(frontier)

        if state in explored:
            continue
        explored.add(state)
        nodes_expanded += 1

        if state.is_goal(goals):
            elapsed = time.time() - start_time
            return {
                "result": "Éxito",
                "solution": reconstruct_path(state),
                "cost": state.cost,
                "nodes_expanded": nodes_expanded,
                "max_frontier": max_frontier,
                "time": elapsed
            }

        for neighbor in get_neighbors(state, sokoban_map):
            if neighbor not in explored:
                h = heuristic(neighbor, goals)
                heapq.heappush(frontier, (h, next(counter), neighbor))
                max_frontier = max(max_frontier, len(frontier))

    elapsed = time.time() - start_time
    return {
        "result": "Fracaso",
        "solution": [],
        "cost": None,
        "nodes_expanded": nodes_expanded,
        "max_frontier": max_frontier,
        "time": elapsed
    }