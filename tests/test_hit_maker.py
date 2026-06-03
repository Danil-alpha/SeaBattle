import pytest
from field import Field, CellState
from hit_maker import HitMaker, HitState


class TestHitMaker:
    def test_hit_miss(self, classic_field):
        hm = HitMaker()
        result = hm.hit(classic_field, 0, 0)
        assert result == HitState.MISS
        assert classic_field.get_cell(0, 0).state == CellState.MISS

    def test_hit_already_missed(self, classic_field):
        hm = HitMaker()
        classic_field.set_cell_state(1, 1, CellState.MISS)
        result = hm.hit(classic_field, 1, 1)
        assert result == HitState.MISS

    def test_hit_already_hit(self, classic_field):
        hm = HitMaker()
        classic_field.set_cell_state(2, 2, CellState.HIT)
        result = hm.hit(classic_field, 2, 2)
        assert result == HitState.ERR

    def test_hit_ship(self, classic_field):
        hm = HitMaker()
        classic_field.addBoard([(3, 3), (3, 4)])
        classic_field.set_cell_state(3, 3, CellState.SHIP)
        classic_field.set_cell_state(3, 4, CellState.SHIP)
        result = hm.hit(classic_field, 3, 3)
        assert result == HitState.HIT
        assert classic_field.get_cell(3, 3).state == CellState.HIT
        result2 = hm.hit(classic_field, 3, 4)
        assert result2 == HitState.CRUSHED
        assert classic_field.get_cell(3, 4).state == CellState.HIT
        neighbors = [(2, 2), (2, 3), (2, 4), (3, 2), (3, 5), (4, 2), (4, 3), (4, 4)]
        for q, r in neighbors:
            if classic_field.is_valid_cell(q, r):
                assert classic_field.get_cell(q, r).state in (
                    CellState.MISS,
                    CellState.EMPTY,
                )

    def test_fill_cells_around_ship(self, classic_field):
        hm = HitMaker()
        ship_coords = [(5, 5), (5, 6)]
        classic_field.addBoard(ship_coords)
        ship = classic_field.boards[0]
        for q, r in ship_coords:
            classic_field.set_cell_state(q, r, CellState.HIT)
        hm.fill_cells_around_ship(classic_field, ship)
        for q, r in [(4, 4), (4, 5), (4, 6), (5, 4), (5, 7), (6, 4), (6, 5), (6, 6)]:
            if classic_field.is_valid_cell(q, r):
                assert classic_field.get_cell(q, r).state == CellState.MISS
