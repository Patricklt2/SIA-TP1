class SokobanMap:
    def __init__(self, walls, goals, boxes, player):
        self.walls = walls
        self.goals = goals
        self.boxes = boxes
        self.player = player

    def __repr__(self):
        return f"<SokobanMap player={self.player} boxes={len(self.boxes)} goals={len(self.goals)}>"

class SokobanState:
    def __init__(self, player, boxes, parent=None, move=None, cost=0):
        self.player = player
        self.boxes = frozenset(boxes)
        self.parent = parent
        self.move = move
        self.cost = cost

    def is_goal(self, goals):
        return self.boxes == goals

    def __hash__(self):
        return hash((self.player, self.boxes))

    def __eq__(self, other):
        return (self.player, self.boxes) == (other.player, other.boxes)

def parse_map(filepath):
    walls = set()
    goals = set()
    boxes = set()
    player = None

    with open(filepath, "r") as f:
        lines = [line.rstrip("\n") for line in f]

    for r, line in enumerate(lines):
        for c, ch in enumerate(line):
            pos = (r, c)
            if ch == "#":
                walls.add(pos)
            elif ch == ".":
                goals.add(pos)
            elif ch == "$":
                boxes.add(pos)
            elif ch == "@":
                player = pos
            elif ch == "*":
                boxes.add(pos)
                goals.add(pos)
            elif ch == "+":
                player = pos
                goals.add(pos)

    if player is None:
        raise ValueError("Mapa inválido: no se encontró jugador '@' o '+'.")

    return SokobanMap(walls, goals, boxes, player)

def get_neighbors(state, sokoban_map):
    moves = [(-1,0,'Up'), (1,0,'Down'), (0,-1,'Left'), (0,1,'Right')]
    neighbors = []

    for dr, dc, action in moves:
        new_r = state.player[0] + dr
        new_c = state.player[1] + dc
        new_pos = (new_r, new_c)

        if new_pos in sokoban_map.walls:
            continue

        new_boxes = set(state.boxes)
        if new_pos in state.boxes:
            box_r = new_r + dr
            box_c = new_c + dc
            new_box_pos = (box_r, box_c)
            if new_box_pos in sokoban_map.walls or new_box_pos in state.boxes:
                continue
            new_boxes.remove(new_pos)
            new_boxes.add(new_box_pos)

        neighbors.append(SokobanState(new_pos, new_boxes, parent=state, move=action, cost=state.cost+1))

    return neighbors

def is_deadlock(state, sokoban_map):
    for box in state.boxes:
        if box in sokoban_map.goals:
            continue

        r, c = box
        walls = sokoban_map.walls

        if ((r-1, c) in walls or (r+1, c) in walls) and \
           ((r, c-1) in walls or (r, c+1) in walls):
            return True

    return False

def reconstruct_path(state):
    path = []
    while state.parent is not None:
        path.append(state.move)
        state = state.parent
    return list(reversed(path))