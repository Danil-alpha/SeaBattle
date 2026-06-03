from random import choice, shuffle
from field import CellState
from hit_maker import HitState


class Bot:
    def __init__(self, bot_type="smart"):
        self.bot_type = bot_type
        self.enemy_field = None
        if bot_type == "smart":
            self.ai = SmartBotAI()
        else:
            self.ai = RandomBotAI()

    def set_enemy_field(self, field):
        self.enemy_field = field
        self.ai.init(field)

    def make_move(self):
        return self.ai.get_next_target()

    def update(self, q, r, result):
        self.ai.update(q, r, result)


class RandomBotAI:
    def init(self, field):
        self.field = field

    def get_next_target(self):
        candidates = [
            (q, r)
            for (q, r), cell in self.field.cells.items()
            if cell.state not in (CellState.HIT, CellState.MISS)
        ]
        if candidates:
            return choice(candidates)
        return None

    def update(self, q, r, result):
        pass


class SmartBotAI:
    def init(self, field):
        self.field = field
        self.mode = "hunt"
        self.target_queue = []
        self.last_hit = None

    def get_next_target(self):
        if self.mode == "target" and self.target_queue:
            return self.target_queue.pop(0)
        candidates = [
            (q, r)
            for (q, r), cell in self.field.cells.items()
            if cell.state not in (CellState.HIT, CellState.MISS)
        ]
        if candidates:
            return choice(candidates)
        return None

    def update(self, q, r, result):
        if result == HitState.MISS:
            return
        if result == HitState.HIT:
            self.mode = "target"
            self.last_hit = (q, r)
            self._add_adjacent_targets(q, r)
        elif result == HitState.CRUSHED:
            self.mode = "hunt"
            self.target_queue.clear()
            self.last_hit = None

    def _add_adjacent_targets(self, q, r):
        neighbors = self.field.get_neighbors(q, r, include_diagonals=False)
        shuffle(neighbors)
        for nq, nr in neighbors:
            cell = self.field.get_cell(nq, nr)
            if cell.state not in (CellState.HIT, CellState.MISS):
                self.target_queue.append((nq, nr))
