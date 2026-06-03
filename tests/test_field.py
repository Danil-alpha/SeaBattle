import pytest
from field import Field, Cell, CellState, Ship


class TestCell:
    def test_initial_state(self):
        cell = Cell(0, 0)
        assert cell.q == 0
        assert cell.r == 0
        assert cell.state == CellState.EMPTY

    def test_str(self):
        cell = Cell(1, 1)
        assert str(cell) == "~"
        cell.state = CellState.SHIP
        assert str(cell) == "S"


class TestShip:
    def test_ship_creation(self):
        coords = [(0, 0), (0, 1), (0, 2)]
        ship = Ship(coords)
        assert ship.size() == 3
        assert ship.hits == 0
        assert not ship.is_crushed()

    def test_hit(self):
        ship = Ship([(0, 0), (1, 0)])
        assert ship.hit(0, 0) is True
        assert ship.hits == 1
        assert not ship.is_crushed()
        assert ship.hit(1, 0) is True
        assert ship.hits == 2
        assert ship.is_crushed()
        assert ship.hit(2, 2) is False


class TestField:
    def test_classic_creation(self, classic_field):
        assert classic_field.width == 10
        assert classic_field.height == 10
        assert len(classic_field.cells) == 100
        assert classic_field.field_type == "classic"
        assert classic_field.is_valid_cell(0, 0)
        assert classic_field.is_valid_cell(9, 9)
        assert not classic_field.is_valid_cell(10, 5)

    def test_hex_creation(self, hex_field):
        assert hex_field.radius == 3
        assert len(hex_field.cells) == 37
        assert hex_field.is_valid_cell(0, 0)
        assert hex_field.is_valid_cell(3, 0)
        assert not hex_field.is_valid_cell(4, 0)

    def test_get_neighbors_classic(self, classic_field):
        center = (1, 1)
        neighbors = classic_field.get_neighbors(*center, include_diagonals=True)
        assert len(neighbors) == 8
        neighbors_no_diag = classic_field.get_neighbors(
            *center, include_diagonals=False
        )
        assert len(neighbors_no_diag) == 4
        edge = (0, 0)
        neighbors_edge = classic_field.get_neighbors(*edge)
        assert len(neighbors_edge) == 3

    def test_get_neighbors_hex(self, hex_field):
        center = (0, 0)
        neighbors = hex_field.get_neighbors(*center)
        assert len(neighbors) == 6
        expected = {(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)}
        assert set(neighbors) == expected
        border = (3, 0)
        neighbors_border = hex_field.get_neighbors(*border)
        assert len(neighbors_border) == 3

    def test_set_cell_state(self, classic_field):
        classic_field.set_cell_state(2, 3, CellState.SHIP)
        assert classic_field.get_cell(2, 3).state == CellState.SHIP

    def test_add_board_and_live_ships(self, classic_field):
        ship_cells = [(1, 1), (1, 2), (1, 3)]
        classic_field.addBoard(ship_cells)
        assert classic_field.hasLiveShips() is True
        ship = classic_field.boards[0]
        ship.hits = 3
        assert classic_field.hasLiveShips() is False

    def test_hit_ship(self, classic_field):
        classic_field.addBoard([(0, 0), (0, 1)])
        ship = classic_field.hitShip(0, 0)
        assert ship is not None
        assert ship.hits == 1
        assert not ship.is_crushed()
        classic_field.hitShip(0, 1)
        assert ship.is_crushed()
        assert classic_field.hitShip(5, 5) is None
