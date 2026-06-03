from field import CellState
from enum import Enum


class HitState(Enum):
    MISS = 0
    CRUSHED = 1
    HIT = 2
    ERR = 3


class HitMaker:
    @staticmethod
    def fill_cells_around_ship(field, ship):
        for q, r in ship.coordinate:
            for nq, nr in field.get_neighbors(q, r):
                cell = field.get_cell(nq, nr)
                if cell and cell.state != CellState.HIT:
                    field.set_cell_state(nq, nr, CellState.MISS)

    def hit(self, field, q, r) -> HitState:
        cell = field.get_cell(q, r)
        if cell.state == CellState.SHIP:
            field.set_cell_state(q, r, CellState.HIT)
            ship = field.hitShip(q, r)
            if ship.is_crushed():
                self.fill_cells_around_ship(field, ship)
                return HitState.CRUSHED
            else:
                return HitState.HIT
        elif cell.state == CellState.HIT:
            return HitState.ERR
        else:
            if cell.state not in (CellState.HIT, CellState.MISS):
                field.set_cell_state(q, r, CellState.MISS)
        return HitState.MISS
