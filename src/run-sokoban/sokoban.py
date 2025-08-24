class SokobanMap:
    def __init__(self, walls, goals, boxes, player):
        self.walls = walls
        self.goals = goals
        self.boxes = boxes
        self.player = player

    def __repr__(self):
        return f"<SokobanMap player={self.player} boxes={len(self.boxes)} goals={len(self.goals)}>"

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

