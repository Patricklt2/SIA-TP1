import time
from ..sokoban import get_neighbors, reconstruct_path

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
                return {
                    "result": "Éxito",
                    "solution": reconstruct_path(state),
                    "cost": state.cost,
                    "nodes_expanded": nodes_expanded_total + nodes_expanded,
                    "max_frontier": max(max_frontier_total, max_frontier),
                    "time": elapsed
                }

            if depth < depth_limit:
                for neighbor in get_neighbors(state, sokoban_map):
                    if neighbor not in explored:
                        frontier.append((neighbor, depth + 1))
                        max_frontier = max(max_frontier, len(frontier))

        nodes_expanded_total += nodes_expanded
        max_frontier_total = max(max_frontier_total, max_frontier)

    elapsed = time.time() - start_time
    return {
        "result": "Fracaso",
        "solution": [],
        "cost": None,
        "nodes_expanded": nodes_expanded_total,
        "max_frontier": max_frontier_total,
        "time": elapsed
    }