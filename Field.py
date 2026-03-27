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

    def __init__(self):
        self.field = [[Cell(x, y) for x in range(self.SIZE)] for y in range(self.SIZE)]
        self.boards = []

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

    def vragField(self) -> str:
        letters = "   A B C D E F G H I J"
        result = letters + "\n"
        for y in range(10):
            line = f"{y+1}"
            for x in range(10):
                state = self.field[y][x].state
                if state == CellState.HIT:
                    line += "❌"
                elif state == CellState.MISS:
                    line += "⬛"
                else:
                    line += "⬜"
            result += line + "\n"
        return result

    def __str__(self) -> str:
        letters = "   A B C D E F G H I J"
        result = letters + "\n"
        for y in range(10):
            line = f"{y + 1}"
            for x in range(10):
                state = self.field[y][x].state
                if state == CellState.SHIP:
                    line += "🚢"
                elif state == CellState.HIT:
                    line += "❌"
                elif state == CellState.MISS:
                    line += "⬛"
                else:
                    line += "⬜"
            result += line + "\n"
        return result

    def hasLiveShips(self) -> bool:
        if not self.boards:
            return False
        for ship in self.boards:
            if not ship.is_crushed():
                return True
        return False
