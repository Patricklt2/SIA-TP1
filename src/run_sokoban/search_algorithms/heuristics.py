# Admisibles
def manhattan_distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def manhattan_heuristic(state, goals):
    total = 0
    for box in state.boxes:
        total += min(manhattan_distance(box.pos, goal) for goal in goals)
    return total

def heuristic_boxes_out(state, goals):
    return sum(1 for b in state.boxes if b.pos not in goals)

# No Admisibles

def player_boxes(state, goals):
    total = 0
    for box in state.boxes:
        dist_to_goal = min(abs(box.pos[0]-g[0]) + abs(box.pos[1]-g[1]) for g in goals)
        dist_to_player = abs(box.pos[0]-state.player[0]) + abs(box.pos[1]-state.player[1])
        total += dist_to_goal + dist_to_player
    return total