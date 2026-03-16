from random import randint
from BattleMaster import *


class HitState(Enum):
    MISS = 0
    CRUSHED = 1
    HIT = 2


class HitMaker:
    def fillCellsAroundShip(self, field: Field, ship: Ship):
        for x, y in ship.coordinate:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx = x + dx
                    ny = y + dy
                    if 0 <= nx < field.SIZE and 0 <= ny < field.SIZE:
                        if field[nx][ny].state != CellState.HIT:
                            field[nx][ny].state = CellState.MISS

    def hit(self, field: Field, x, y) -> HitState:
        if field[x][y].state == CellState.SHIP:
            field[x][y].state = CellState.HIT
            ship = field.hitShip(x, y)
            if ship.is_crushed():
                self.fillCellsAroundShip(field, ship)
                return HitState.CRUSHED
            else:
                return HitState.HIT
        return HitState.MISS

    def randomHit(self, field: Field):
        while True:
            x = randint(0, 9)
            y = randint(0, 9)
            if field[x][y].state != CellState.HIT and field[x][y].state != CellState.MISS:
                return self.hit(field, x, y)
