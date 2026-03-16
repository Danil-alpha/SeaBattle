from random import randint

from Field import *


class ShipPlacer:
    def __init__(self):
        self.countShips = {1: 4, 2: 3, 3: 2, 4: 1}

    def howManyShips(self):
        return self.countShips

    def setBufferAroundShip(self, field: Field, x1: int, y1: int, x2: int, y2: int):
        for x in range(min(x1, x2) - 1, max(x1, x2) + 2):
            for y in range(min(y1, y2) - 1, max(y1, y2) + 2):
                if 0 <= x < 10 and 0 <= y < 10 and field[x][y].state == CellState.EMPTY:
                    field[x][y].state = CellState.BUFFER

    def checkNumberOfShips(self, x1, y1, x2, y2):
        length = max(abs(x1 - x2), abs(y1 - y2))
        if self.countShips[length] == 0:
            return False
        self.countShips[length] -= 1
        return True

    def setBoard(self, field: Field, x1: int, y1: int, x2: int = None, y2: int = None):
        if x2 is None or y2 is None:
            x2 = x1
            y2 = y1

        if (x1 != x2 and y1 != y2 or not (0 <= x1 < 10)
                or not (0 <= x2 < 10) or not (0 <= y1 < 10) or not (0 <= y2 < 10)):
            return False
        if not self.checkNumberOfShips(x1, y1, x2, y2):
            return False
        coord = []
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                field[x][y].state = CellState.SHIP
                coord.append((x, y))
        self.setBufferAroundShip(field, x1, x2, y1, y2)
        field.addBoard(coord)
        return True

    def autoSetBoards(self, field: Field):
        for i in range(4, 0, -1):
            while self.countShips[i] != 0:
                self.autoSetBoard(field, i)
                self.countShips[i] -= 1

    def isEmpty(self, field, x1: int, y1: int, x2: int, y2: int):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                if field[x][y].state != CellState.EMPTY:
                    return False
        return True

    def autoSetBoard(self, field: Field, lenShip: int):
        while True:
            orientation = randint(0, 1)
            if orientation == 0:
                x1 = randint(0, 10 - lenShip)
                y1 = randint(0, 9)
                x2 = x1 + lenShip - 1
                y2 = y1
            else:
                x1 = randint(0, 9)
                y1 = randint(0, 10 - lenShip)
                x2 = x1
                y2 = y1 + lenShip - 1
            if self.isEmpty(field, x1, y1, x2, y2):
                coordShip: list[tuple[int, int]] = []
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    for y in range(min(y1, y2), max(y1, y2) + 1):
                        field[x][y].state = CellState.SHIP
                        coordShip.append((x, y))
                self.setBufferAroundShip(field, x1, y1, x2, y2)
                field.boards.append(Ship(coordShip))
                break
