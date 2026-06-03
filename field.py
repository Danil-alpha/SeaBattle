from enum import Enum
import math


class CellState(Enum):
    EMPTY = "~"
    SHIP = "S"
    BUFFER = "-"
    HIT = "X"
    MISS = "•"


class Cell:
    def __init__(self, q, r):
        self.q = q
        self.r = r
        self.state = CellState.EMPTY

    def __str__(self):
        return self.state.value


class Ship:
    def __init__(self, coordinate: list):
        self.coordinate = coordinate
        self.hits = 0

    def size(self):
        return len(self.coordinate)

    def hit(self, q, r):
        if (q, r) in self.coordinate:
            self.hits += 1
            return True
        return False

    def is_crushed(self):
        return len(self.coordinate) == self.hits


class Field:
    def __init__(self, radius=3, field_type="classic", width=None, height=None):
        self.field_type = field_type
        if field_type == "classic":
            self.width = width if width else 10
            self.height = height if height else 10
            self.radius = None
            self.cells = {}
            for x in range(self.width):
                for y in range(self.height):
                    self.cells[(x, y)] = Cell(x, y)
        else:
            self.radius = radius
            self.width = None
            self.height = None
            self.cells = {}
            for q in range(-radius, radius + 1):
                r1 = max(-radius, -q - radius)
                r2 = min(radius, -q + radius)
                for r in range(r1, r2 + 1):
                    self.cells[(q, r)] = Cell(q, r)
        self.boards = []

    def is_valid_cell(self, q, r):
        return (q, r) in self.cells

    def get_neighbors(self, q, r, include_diagonals=True):
        neighbors = []
        if self.field_type == "classic":
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if dx == 0 and dy == 0:
                        continue
                    if not include_diagonals and abs(dx) + abs(dy) == 2:
                        continue
                    nx, ny = q + dx, r + dy
                    if (nx, ny) in self.cells:
                        neighbors.append((nx, ny))
        else:
            directions = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
            for dq, dr in directions:
                nq, nr = q + dq, r + dr
                if (nq, nr) in self.cells:
                    neighbors.append((nq, nr))
        return neighbors

    def get_cell(self, q, r):
        return self.cells.get((q, r))

    def set_cell_state(self, q, r, state):
        if (q, r) in self.cells:
            self.cells[(q, r)].state = state

    def addBoard(self, coord: list):
        self.boards.append(Ship(coord))

    def hitShip(self, q, r):
        for ship in self.boards:
            if (q, r) in ship.coordinate:
                ship.hits += 1
                return ship
        return None

    def hasLiveShips(self):
        if not self.boards:
            return False
        for ship in self.boards:
            if not ship.is_crushed():
                return True
        return False
