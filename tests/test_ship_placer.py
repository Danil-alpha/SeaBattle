import pytest
from field import Field, CellState
from ship_placer import ShipPlacer


class TestShipPlacerBasics:
    def test_how_many_ships(self, classic_placer):
        counts = classic_placer.howManyShips()
        assert counts == {1: 4, 2: 3, 3: 2, 4: 1}

    def test_check_number_of_ships(self, classic_placer):
        assert classic_placer.checkNumberOfShips(4) is True
        assert classic_placer.ship_counts[4] == 0
        assert classic_placer.checkNumberOfShips(4) is False
        assert classic_placer.checkNumberOfShips(5) is False

    def test_is_valid_hex_line(self, hex_placer):
        assert hex_placer._is_valid_hex_line(0, 0, 2, 0) is True
        assert hex_placer._is_valid_hex_line(0, 0, 0, 2) is True
        assert hex_placer._is_valid_hex_line(0, 0, 2, 2) is True
        assert hex_placer._is_valid_hex_line(0, 0, -2, 2) is True
        assert hex_placer._is_valid_hex_line(0, 0, 1, 2) is False
        assert hex_placer._is_valid_hex_line(0, 0, 0, 0) is False


class TestSetBoard:
    def test_set_horizontal_classic(self, classic_field, classic_placer):
        result = classic_placer.setBoard(classic_field, 2, 3, 5, 3)
        assert result is True
        for x in range(2, 6):
            assert classic_field.get_cell(x, 3).state == CellState.SHIP
        assert classic_field.get_cell(1, 2).state == CellState.BUFFER
        assert classic_field.get_cell(6, 3).state == CellState.BUFFER

    def test_set_vertical_classic(self, classic_field, classic_placer):
        result = classic_placer.setBoard(classic_field, 4, 1, 4, 3)
        assert result is True
        for y in range(1, 4):
            assert classic_field.get_cell(4, y).state == CellState.SHIP

    def test_set_invalid_diagonal_classic(self, classic_field, classic_placer):
        result = classic_placer.setBoard(classic_field, 0, 0, 2, 2)
        assert result is False

    def test_set_hex_line(self, hex_field, hex_placer):
        result = hex_placer.setBoard(hex_field, 0, 0, 2, 0)
        assert result is True
        assert hex_field.get_cell(0, 0).state == CellState.SHIP
        assert hex_field.get_cell(1, 0).state == CellState.SHIP
        assert hex_field.get_cell(2, 0).state == CellState.SHIP
        neighbor = hex_field.get_cell(0, -1)
        if neighbor:
            assert neighbor.state == CellState.BUFFER

    def test_set_ship_overlap(self, classic_field, classic_placer):
        classic_placer.setBoard(classic_field, 0, 0, 0, 2)
        result = classic_placer.setBoard(classic_field, 0, 1, 0, 3)
        assert result is False

    def test_set_ship_too_long(self, classic_field, classic_placer):
        result = classic_placer.setBoard(classic_field, 0, 0, 0, 10)
        assert result is False

    def test_set_board_invalid_hex_line(self, hex_field, hex_placer):
        assert hex_placer.setBoard(hex_field, 0, 0, 1, 2) is False
        assert hex_placer.setBoard(hex_field, 3, 0, 4, 0) is False

    def test_set_board_invalid_cell_classic(self, classic_field, classic_placer):
        assert classic_placer.setBoard(classic_field, -1, 0, 2, 0) is False

    def test_set_board_invalid_cell_hex(self, hex_field, hex_placer):
        assert hex_placer.setBoard(hex_field, -4, 0, -2, 0) is False


class TestAutoSetBoards:
    def test_auto_classic(self, classic_field, classic_placer):
        result = classic_placer.autoSetBoards(classic_field)
        assert result is True
        total_ships = len(classic_field.boards)
        expected_total = sum(classic_placer.original_counts.values())
        assert total_ships == expected_total

    def test_auto_hex(self):
        field = Field(field_type="hex", radius=2)
        tiny_counts = {2: 1, 1: 2}
        placer = ShipPlacer(field_type="hex", radius=2, ship_counts=tiny_counts)
        result = placer.autoSetBoards(field)
        assert result is True
        total_ships = len(field.boards)
        expected_total = sum(tiny_counts.values())
        assert total_ships == expected_total

    def test_auto_failure_on_small_field(self):
        small_field = Field(field_type="classic", width=2, height=2)
        placer = ShipPlacer(field_type="classic", width=2, height=2, ship_counts={3: 1})
        result = placer.autoSetBoards(small_field)
        assert result is False


class TestShipPlacerAdvanced:
    def test_generate_all_positions(self, hex_field):
        placer = ShipPlacer(field_type="hex", radius=3)
        positions = placer._generate_all_positions(hex_field, 2)
        assert len(positions) > 0
        for pos in positions:
            assert len(pos) == 2
            for q, r in pos:
                assert hex_field.is_valid_cell(q, r)

    def test_remove_ship_isolated(self, classic_field):
        placer = ShipPlacer(field_type="classic", width=10, height=10)
        assert placer.setBoard(classic_field, 0, 0, 0, 2)
        ship = classic_field.boards[0]
        placer._remove_ship(classic_field, ship.coordinate)
        assert len(classic_field.boards) == 0
        for q, r in ship.coordinate:
            assert classic_field.get_cell(q, r).state == CellState.EMPTY

    def test_remove_ship_with_shared_buffer(self, classic_field):
        placer = ShipPlacer(field_type="classic", width=10, height=10)
        assert placer.setBoard(classic_field, 1, 1, 3, 1)
        assert placer.setBoard(classic_field, 2, 3, 2, 4)
        first_ship = classic_field.boards[0]
        placer._remove_ship(classic_field, first_ship.coordinate)
        second_ship = classic_field.boards[0]
        assert second_ship is not None
        shared_buffer = (2, 2)
        assert classic_field.get_cell(*shared_buffer).state == CellState.BUFFER
        for q, r in first_ship.coordinate:
            assert classic_field.get_cell(q, r).state == CellState.EMPTY

    def test_auto_set_board_classic_vertical_orientation(self):
        field = Field(field_type="classic", width=10, height=10)
        placer = ShipPlacer(
            field_type="classic", width=10, height=10, ship_counts={2: 5}
        )
        result = placer._autoSetBoard(field, 2)
        assert result is True

    def test_auto_set_board_hex_with_axis(self):
        field = Field(field_type="hex", radius=2)
        placer = ShipPlacer(field_type="hex", radius=2, ship_counts={2: 3})
        result1 = placer._autoSetBoard(field, 2)
        result2 = placer._autoSetBoard(field, 2)
        assert result1 is True
        assert result2 is True
