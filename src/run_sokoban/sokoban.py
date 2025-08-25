from collections import deque

class SokobanMap:
    def __init__(self, walls, goals, boxes, player, floors):
        self.walls = walls
        self.goals = goals
        self.boxes = boxes
        self.player = player
        self.floors = floors

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
    floors = set()

    with open(filepath, "r") as f:
        lines = [line.rstrip("\n") for line in f]

    for r, line in enumerate(lines):
        for c, ch in enumerate(line):
            pos = (r, c)
            if ch == "#":
                walls.add(pos)
            else:
                floors.add(pos)
                if ch == ".":
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

    return SokobanMap(walls, goals, boxes, player, floors)

def get_neighbors(state, sokoban_map, dead_squares):
    moves = [(-1,0,'Up'), (1,0,'Down'), (0,-1,'Left'), (0,1,'Right')]
    neighbors = []

    walls = sokoban_map.walls
    goals = sokoban_map.goals
    boxes = state.boxes

    for dr, dc, action in moves:
        new_r = state.player[0] + dr
        new_c = state.player[1] + dc
        new_pos = (new_r, new_c)

        if new_pos in walls:
            continue

        new_boxes = set(boxes)
        if new_pos in boxes:
            box_r = new_r + dr
            box_c = new_c + dc
            new_box_pos = (box_r, box_c)

            if new_box_pos in walls or new_box_pos in boxes:
                continue

            if new_box_pos in dead_squares and new_box_pos not in goals:
                continue

            if ((box_r-1, box_c) in walls and (box_r, box_c-1) in walls) or \
               ((box_r-1, box_c) in walls and (box_r, box_c+1) in walls) or \
               ((box_r+1, box_c) in walls and (box_r, box_c-1) in walls) or \
               ((box_r+1, box_c) in walls and (box_r, box_c+1) in walls):
                continue

            squares = [(box_r, box_c), (box_r+1, box_c), (box_r, box_c+1), (box_r+1, box_c+1)]
            if all(s not in goals and (s in walls or s in boxes) for s in squares):
                continue
            squares = [(box_r, box_c), (box_r-1, box_c), (box_r, box_c-1), (box_r-1, box_c-1)]
            if all(s not in goals and (s in walls or s in boxes) for s in squares):
                continue

            new_boxes.remove(new_pos)
            new_boxes.add(new_box_pos)

        neighbors.append(SokobanState(new_pos, new_boxes, parent=state, move=action, cost=state.cost+1))

    return neighbors

def reconstruct_path(state):
    path = []
    while state.parent is not None:
        path.append(state.move)
        state = state.parent
    return list(reversed(path))

def precompute_dead_squares(sokoban_map):
    walls = sokoban_map.walls
    floors = sokoban_map.floors
    goals = sokoban_map.goals
    
    dead_squares = set()
    
    for r, c in floors:
        if (r, c) in goals:
            continue

        exits = sum((r+dr, c+dc) not in walls for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)])
        if exits == 1:
            dead_squares.add((r, c))
            continue

        is_corner = (
            ((r-1, c) in walls and (r, c-1) in walls) or
            ((r-1, c) in walls and (r, c+1) in walls) or
            ((r+1, c) in walls and (r, c-1) in walls) or
            ((r+1, c) in walls and (r, c+1) in walls)
        )
        if is_corner:
            near_goal = any((r+dr, c+dc) in goals for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)])
            if not near_goal:
                dead_squares.add((r, c))
    
    return dead_squares