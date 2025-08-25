import time
from collections import deque
from ..sokoban import get_neighbors
from .utils import get_result

def bfs(initial_state, goals, sokoban_map, dead_squares, neighbor_finder):
    start_time = time.time()
    frontier = deque([initial_state])
    explored = set()
    max_frontier = 1
    nodes_expanded = 0

    while frontier:
        state = frontier.popleft()
        if state.is_goal(goals):
            elapsed = time.time() - start_time
            return get_result(state, nodes_expanded, max_frontier, start_time, success=True)

        explored.add(state)
        nodes_expanded += 1
        for neighbor in neighbor_finder(state, sokoban_map, dead_squares):
            if neighbor not in explored and neighbor not in frontier:
                frontier.append(neighbor)
                max_frontier = max(max_frontier, len(frontier))

    elapsed = time.time() - start_time
    return get_result(None, nodes_expanded, max_frontier, start_time, success=False)