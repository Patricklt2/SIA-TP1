import time
import heapq
import itertools
from ..sokoban import get_neighbors, is_deadlock
from .utils import get_result

def astar(initial_state, sokoban_map, heuristic, dead_squares):
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
            return get_result(state, nodes_expanded, max_frontier, start_time, success=True)

        for neighbor in get_neighbors(state, sokoban_map):
            if neighbor not in explored and not is_deadlock(neighbor, sokoban_map, dead_squares):
                g = neighbor.cost
                h = heuristic(neighbor, goals)
                heapq.heappush(frontier, (g + h, next(counter), neighbor))
                max_frontier = max(max_frontier, len(frontier))

    elapsed = time.time() - start_time
    return get_result(None, nodes_expanded, max_frontier, start_time, success=False)