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
        return self.state.value


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
    def __init__(self, width=10, height=10):
        self.width = width
        self.height = height
        # поле: [y][x] — y строка, x столбец
        self.field = [[Cell(x, y) for x in range(self.width)] for y in range(self.height)]
        self.boards = []

    def __getitem__(self, y: int):
        return self.field[y]

    def checkCell(self, x: int, y: int) -> Cell:
        return self.field[y][x]

    def addBoard(self, coord: list):
        self.boards.append(Ship(coord))

    def hitShip(self, x, y) -> Ship:
        for ship in self.boards:
            if (x, y) in ship.coordinate:
                ship.hits += 1
                return ship
        return None

    def _col_letter(self, idx):
        if self.width <= 26:
            return chr(ord('A') + idx)
        else:
            return str(idx + 1)

    def vragField(self) -> str:
        header = "   " + " ".join(self._col_letter(i) for i in range(self.width))
        result = header + "\n"
        for y in range(self.height):
            line = f"{y + 1:2}"
            for x in range(self.width):
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
        header = "   " + " ".join(self._col_letter(i) for i in range(self.width))
        result = header + "\n"
        for y in range(self.height):
            line = f"{y + 1:2}"
            for x in range(self.width):
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
