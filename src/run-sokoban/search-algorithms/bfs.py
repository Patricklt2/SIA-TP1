import time
from collections import deque
from sokoban import reconstruct_path, get_neighbors

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
            return {
                "result": "Éxito",
                "solution": reconstruct_path(state),
                "cost": state.cost,
                "nodes_expanded": nodes_expanded,
                "max_frontier": max_frontier,
                "time": elapsed
            }

        explored.add(state)
        nodes_expanded += 1
        for neighbor in get_neighbors(state, sokoban_map):
            if neighbor not in explored and neighbor not in frontier:
                frontier.append(neighbor)
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