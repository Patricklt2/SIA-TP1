from collections import deque

class Box:
    def __init__(self, box_id, pos):
        self.id = box_id
        self.pos = pos

    def __hash__(self):
        return hash((self.id, self.pos))

    def __eq__(self, other):
        return isinstance(other, Box) and self.id == other.id and self.pos == other.pos

    def __repr__(self):
        return f"Box(id={self.id}, pos={self.pos})"

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
        return {b.pos for b in self.boxes} == goals

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

    box_counter = 1

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
                    boxes.add(Box(box_counter, pos))
                    box_counter += 1
                elif ch == "@":
                    player = pos
                elif ch == "*":
                    boxes.add(Box(box_counter, pos))
                    box_counter += 1
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

        box_to_move = next((b for b in boxes if b.pos == new_pos), None)
        if box_to_move:
            new_box_pos = (box_to_move.pos[0]+dr, box_to_move.pos[1]+dc)

            if new_box_pos in walls or any(b.pos == new_box_pos for b in boxes):
                continue

            if new_box_pos in dead_squares and new_box_pos not in goals:
                continue

            if is_box_stuck(new_box_pos, {b.pos for b in new_boxes - {box_to_move}} | {new_box_pos}, walls, goals):
                continue

            squares = [
                (new_box_pos[0], new_box_pos[1]),
                (new_box_pos[0]+1, new_box_pos[1]),
                (new_box_pos[0], new_box_pos[1]+1),
                (new_box_pos[0]+1, new_box_pos[1]+1)
            ]
            if all(s not in goals and (s in walls or any(b.pos == s for b in boxes)) for s in squares):
                continue

            squares = [
                (new_box_pos[0], new_box_pos[1]),
                (new_box_pos[0]-1, new_box_pos[1]),
                (new_box_pos[0], new_box_pos[1]-1),
                (new_box_pos[0]-1, new_box_pos[1]-1)
            ]
            if all(s not in goals and (s in walls or any(b.pos == s for b in boxes)) for s in squares):
                continue

            # Replace the moved box with updated position, keeping the same ID
            new_boxes.remove(box_to_move)
            new_boxes.add(Box(box_to_move.id, new_box_pos))

        # Record move as (action, box_id or None)
        move_record = (action, box_to_move.id if box_to_move else None)
        neighbors.append(SokobanState(new_pos, new_boxes, parent=state, move=move_record, cost=state.cost+1))

    return neighbors

def is_box_stuck(box_pos, boxes, walls, goals):
    if box_pos in goals:
        return False
    
    r, c = box_pos
    directions = [(-1,0), (1,0), (0,-1), (0,1)]
    
    for dr, dc in directions:
        target = (r+dr, c+dc)
        if target not in walls and target not in boxes:
            return False
    return True

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

def compute_reachable(player, boxes, walls):
    box_positions = {box.pos for box in boxes}
    reachable = set()
    queue = deque([player])
    while queue:
        pos = queue.popleft()
        if pos in reachable:
            continue
        reachable.add(pos)
        r, c = pos
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            new_pos = (r+dr, c+dc)
            if new_pos not in walls and new_pos not in box_positions and new_pos not in reachable:
                queue.append(new_pos)
    return reachable

def get_push_neighbors(state, sokoban_map, dead_squares):
    directions = [(-1,0,'Up'), (1,0,'Down'), (0,-1,'Left'), (0,1,'Right')]
    neighbors = []

    walls = sokoban_map.walls
    goals = sokoban_map.goals
    boxes = state.boxes

    box_positions = {b.pos for b in boxes}
    reachable = compute_reachable(state.player, boxes, walls)

    for box in boxes:
        for dr, dc, move in directions:
            push_from = (box.pos[0]-dr, box.pos[1]-dc)
            new_box_pos = (box.pos[0]+dr, box.pos[1]+dc)

            if push_from not in reachable:
                continue

            if new_box_pos in walls or new_box_pos in box_positions:
                continue

            if new_box_pos in dead_squares and new_box_pos not in goals:
                continue

            updated_boxes = {b if b.id != box.id else Box(b.id, new_box_pos) for b in boxes}

            if is_box_stuck(new_box_pos, {b.pos for b in updated_boxes}, walls, goals):
                continue

            new_player_pos = box.pos
            move_record = (move, box.id)
            neighbors.append(SokobanState(new_player_pos, updated_boxes, parent=state, move=move_record, cost=state.cost+1))

    return neighbors