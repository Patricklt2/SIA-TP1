import time
from ..sokoban import get_neighbors, is_deadlock
from .utils import get_result

def iddfs(initial_state, sokoban_map, max_depth=50):
    start_time = time.time()
    goals = sokoban_map.goals
    nodes_expanded_total = 0
    max_frontier_total = 0

    for depth_limit in range(1, max_depth + 1):
        frontier = [(initial_state, 0)]
        explored = set()
        max_frontier = 1
        nodes_expanded = 0

        while frontier:
            state, depth = frontier.pop()
            if state in explored:
                continue
            explored.add(state)
            nodes_expanded += 1

            if state.is_goal(goals):
                elapsed = time.time() - start_time
                return get_result(state, nodes_expanded, max_frontier, start_time, success=True)

            if depth < depth_limit:
                for neighbor in get_neighbors(state, sokoban_map):
                    if neighbor not in explored and not is_deadlock(neighbor, sokoban_map):
                        frontier.append((neighbor, depth + 1))
                        max_frontier = max(max_frontier, len(frontier))

        nodes_expanded_total += nodes_expanded
        max_frontier_total = max(max_frontier_total, max_frontier)

    elapsed = time.time() - start_time
    return get_result(None, nodes_expanded, max_frontier, start_time, success=False)