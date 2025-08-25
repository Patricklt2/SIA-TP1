import time
from ..sokoban import reconstruct_path

def get_result(state, nodes_expanded, max_frontier, start_time, success=True):
    elapsed = time.time() - start_time
    if success:
        return {
            "result": "Éxito",
            "solution": reconstruct_path(state),
            "cost": state.cost,
            "nodes_expanded": nodes_expanded,
            "max_frontier": max_frontier,
            "time": elapsed
        }
    else:
        return {
            "result": "Fracaso",
            "solution": [],
            "cost": None,
            "nodes_expanded": nodes_expanded,
            "max_frontier": max_frontier,
            "time": elapsed
        }