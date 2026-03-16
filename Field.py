from enum import Enum


class CellState(Enum):
    EMPTY = "~"
    SHIP = "S"
    BUFFER = "-"
    HIT = "X"
    MISS = "•"


class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.state = CellState.EMPTY

    def __str__(self):
        return self.state


class Ship:
    def __init__(self, coordinate: list):
        self.coordinate = coordinate
        self.hits = 0

    def size(self):
        return len(self.coordinate)

    def hit(self, x, y):
        if (x, y) in self.coordinate:
            self.hits += 1
            return True
        return False

    def is_crushed(self):
        return len(self.coordinate) == self.hits


class Field:
    SIZE = 10
    boards = []

    def __init__(self):
        self.field = [[Cell(x, y) for x in range(self.SIZE)] for y in range(self.SIZE)]

    def __getitem__(self, y: int):
        return self.field[y]

    def checkCell(self, x: int, y: int) -> Cell:
        return self.field[x][y]

    def addBoard(self, coord: list):
        self.boards.append(Ship(coord))

    def hitShip(self, x, y) -> Ship:
        for ship in self.boards:
            if (x, y) in ship.coordinate:
                ship.hits += 1
                return ship
        return None
