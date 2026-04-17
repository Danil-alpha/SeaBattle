from random import randint, choice, shuffle
from Field import *
from enum import Enum


class HitState(Enum):
    MISS = 0
    CRUSHED = 1
    HIT = 2
    ERR = 3


class BotAI:
    def __init__(self, field: Field):
        self.field = field
        self.mode = "hunt"
        self.target_queue = []
        self.last_hit = None

    def getNextTarget(self):
        if self.mode == "target" and self.target_queue:
            return self.target_queue.pop(0)
        candidates = []
        for y in range(self.field.height):
            for x in range(self.field.width):
                if (x + y) % 2 == 0:
                    cell = self.field[y][x]
                    if cell.state not in (CellState.HIT, CellState.MISS):
                        candidates.append((x, y))
        if not candidates:
            for y in range(self.field.height):
                for x in range(self.field.width):
                    cell = self.field[y][x]
                    if cell.state not in (CellState.HIT, CellState.MISS):
                        candidates.append((x, y))
        if candidates:
            return choice(candidates)
        return None

    def update(self, x, y, result: HitState):
        if result == HitState.MISS:
            return
        if result == HitState.HIT:
            self.mode = "target"
            self.last_hit = (x, y)
            self._addAdjacentTargets(x, y)
        elif result == HitState.CRUSHED:
            self.mode = "hunt"
            self.target_queue.clear()
            self.last_hit = None

    def _addAdjacentTargets(self, x, y):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.field.width and 0 <= ny < self.field.height:
                cell = self.field[ny][nx]
                if cell.state not in (CellState.HIT, CellState.MISS):
                    self.target_queue.append((nx, ny))


class HitMaker:
    def __init__(self):
        self.bot_ai = None

    def initBotAI(self, field: Field):
        self.bot_ai = BotAI(field)

    def fillCellsAroundShip(self, field: Field, ship: Ship):
        for x, y in ship.coordinate:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < field.width and 0 <= ny < field.height:
                        if field[ny][nx].state != CellState.HIT:
                            field[ny][nx].state = CellState.MISS

    def hit(self, field: Field, x, y) -> HitState:
        if field[y][x].state == CellState.SHIP:
            field[y][x].state = CellState.HIT
            ship = field.hitShip(x, y)
            if ship.is_crushed():
                self.fillCellsAroundShip(field, ship)
                return HitState.CRUSHED
            else:
                return HitState.HIT
        elif field[y][x].state == CellState.HIT:
            return HitState.ERR
        else:
            if field[y][x].state not in (CellState.HIT, CellState.MISS):
                field[y][x].state = CellState.MISS
        return HitState.MISS

    def randomHit(self, field: Field):
        while True:
            x = randint(0, field.width - 1)
            y = randint(0, field.height - 1)
            if field[y][x].state != CellState.HIT and field[y][x].state != CellState.MISS:
                return self.hit(field, x, y)

    def smartHit(self, field: Field) -> HitState:
        if not self.bot_ai:
            self.initBotAI(field)
        target = self.bot_ai.getNextTarget()
        if target is None:
            return HitState.ERR
        x, y = target
        result = self.hit(field, x, y)
        self.bot_ai.update(x, y, result)
        return result
