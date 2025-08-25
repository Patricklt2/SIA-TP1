import time
from collections import deque
from ..sokoban import get_neighbors, is_deadlock
from .utils import get_result

def bfs(initial_state, goals, sokoban_map):
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
        for neighbor in get_neighbors(state, sokoban_map):
            if neighbor not in explored and neighbor not in frontier and not is_deadlock(neighbor, sokoban_map):
                frontier.append(neighbor)
                max_frontier = max(max_frontier, len(frontier))

    elapsed = time.time() - start_time
    return get_result(None, nodes_expanded, max_frontier, start_time, success=False)