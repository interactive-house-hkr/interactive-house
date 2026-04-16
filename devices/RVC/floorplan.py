from collections import deque

GRID_SIZE = 8
DOCK_POSITION = (0, 0)

ROOMS = {
    "Bedroom": {(x, y) for x in range(0, 3) for y in range(0, 5)},
    "Kitchen": {(x, y) for x in range(0, 3) for y in range(5, 8)},
    "Living Room": {(x, y) for x in range(3, 8) for y in range(4, 8)},
    "Hall": {(x, y) for x in range(3, 5) for y in range(0, 4)},
    "Bathroom": {(x, y) for x in range(5, 8) for y in range(0, 4)},
}

FURNITURE = {
    "bed": {(0, 2), (1, 2)},
    "counter": {(0, 7), (1, 7), (2, 7)},
    "sofa": {(4, 6), (5, 6)},
    "table": {(6, 5)},
    "sink": {(6, 2)},
}

ALL_ROOM_CELLS = set().union(*ROOMS.values())
OBSTACLES = set().union(*FURNITURE.values())
WALKABLE_CELLS = ALL_ROOM_CELLS - OBSTACLES

DOORS = {
    frozenset(((2, 1), (3, 1))),  # Bedroom <-> Hall
    frozenset(((2, 6), (3, 6))),  # Kitchen <-> Living Room
    frozenset(((4, 3), (4, 4))),  # Hall <-> Living Room
    frozenset(((4, 2), (5, 2))),  # Hall <-> Bathroom
}

ENTRY_DOOR = ("south", (3, 0))  # bottom edge of hall cell (3,0)


def room_name(position):
    for name, cells in ROOMS.items():
        if position in cells:
            return name
    return "Unknown"


def is_walkable(position):
    return position in WALKABLE_CELLS


def can_move_between(a, b):
    if a not in WALKABLE_CELLS or b not in WALKABLE_CELLS:
        return False

    if abs(a[0] - b[0]) + abs(a[1] - b[1]) != 1:
        return False

    if room_name(a) == room_name(b):
        return True

    return frozenset((a, b)) in DOORS


def neighbors(position):
    x, y = position
    candidates = [
        (x + 1, y),
        (x - 1, y),
        (x, y + 1),
        (x, y - 1),
    ]
    return [p for p in candidates if can_move_between(position, p)]


def shortest_path(start, goal):
    if start not in WALKABLE_CELLS or goal not in WALKABLE_CELLS:
        return []

    queue = deque([start])
    previous = {start: None}

    while queue:
        current = queue.popleft()

        if current == goal:
            break

        for nxt in neighbors(current):
            if nxt not in previous:
                previous[nxt] = current
                queue.append(nxt)

    if goal not in previous:
        return []

    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = previous[current]

    return list(reversed(path))