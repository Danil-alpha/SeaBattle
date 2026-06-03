# ship_placer.py
from random import randint, choice, shuffle
from field import *


class ShipPlacer:
    def __init__(
            self, field_type="classic", radius=3, width=10, height=10, ship_counts=None
    ):
        self.field_type = field_type
        self.radius = radius
        self.width = width
        self.height = height
        if ship_counts is None:
            self.ship_counts = {1: 4, 2: 3, 3: 2, 4: 1}
        else:
            self.ship_counts = ship_counts.copy()
        self.original_counts = self.ship_counts.copy()
        self.max_backtrack_attempts = 100

    def howManyShips(self):
        return self.ship_counts

    def setBufferAroundShip(self, field: Field, cells):
        for q, r in cells:
            for nq, nr in field.get_neighbors(q, r):
                if field.get_cell(nq, nr).state == CellState.EMPTY:
                    field.set_cell_state(nq, nr, CellState.BUFFER)

    def checkNumberOfShips(self, length: int) -> bool:
        if length not in self.ship_counts or self.ship_counts[length] == 0:
            return False
        self.ship_counts[length] -= 1
        return True

    def _is_valid_hex_line(self, q1, r1, q2, r2):
        if q1 == q2 and r1 == r2:
            return True
        dq = q2 - q1
        dr = r2 - r1
        return (dr == 0) or (dq == 0) or (dq == -dr)

    def setBoard(self, field: Field, q1, r1, q2=None, r2=None):
        if q2 is None or r2 is None:
            q2, r2 = q1, r1

        if not (field.is_valid_cell(q1, r1) and field.is_valid_cell(q2, r2)):
            return False

        if self.field_type == "classic":
            if q1 != q2 and r1 != r2:
                return False
        else:
            if not self._is_valid_hex_line(q1, r1, q2, r2):
                return False

        if self.field_type == "classic":
            cells = []
            for x in range(min(q1, q2), max(q1, q2) + 1):
                for y in range(min(r1, r2), max(r1, r2) + 1):
                    if not field.is_valid_cell(x, y):
                        return False
                    if field.get_cell(x, y).state != CellState.EMPTY:
                        return False
                    cells.append((x, y))
        else:
            dq = 0 if q2 == q1 else (1 if q2 > q1 else -1)
            dr = 0 if r2 == r1 else (1 if r2 > r1 else -1)
            length = max(abs(q1 - q2), abs(r1 - r2)) + 1
            cells = []
            q, r = q1, r1
            for _ in range(length):
                if not field.is_valid_cell(q, r):
                    return False
                if field.get_cell(q, r).state != CellState.EMPTY:
                    return False
                cells.append((q, r))
                q += dq
                r += dr

        length = len(cells)
        if (
                length
                > max(self.width if self.width else 20, self.height if self.height else 20)
                or length < 1
        ):
            return False
        if not self.checkNumberOfShips(length):
            return False

        for q, r in cells:
            field.set_cell_state(q, r, CellState.SHIP)
        self.setBufferAroundShip(field, cells)
        field.addBoard(cells)
        return True

    def autoSetBoards(self, field: Field) -> bool:
        self.ship_counts = self.original_counts.copy()
        if self.field_type == "classic":
            for length in sorted(self.ship_counts.keys(), reverse=True):
                count = self.ship_counts[length]
                for _ in range(count):
                    if not self._autoSetBoard(field, length):
                        return False
            return True
        else:
            ships_to_place = []
            for length, count in self.ship_counts.items():
                for _ in range(count):
                    ships_to_place.append(length)
            ships_to_place.sort(reverse=True)
            return self._backtrack_place(field, ships_to_place)

    def _backtrack_place(self, field: Field, ships):
        if not ships:
            return True
        length = ships[0]
        possible_positions = self._generate_all_positions(field, length)
        shuffle(possible_positions)
        for cells in possible_positions:
            for q, r in cells:
                field.set_cell_state(q, r, CellState.SHIP)
            self.setBufferAroundShip(field, cells)
            field.addBoard(cells)
            if self._backtrack_place(field, ships[1:]):
                return True
            self._remove_ship(field, cells)
        return False

    def _generate_all_positions(self, field: Field, length):
        positions = []
        empty_cells = [
            (q, r)
            for (q, r), cell in field.cells.items()
            if cell.state == CellState.EMPTY
        ]
        directions = [(1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]
        for q, r in empty_cells:
            for dq, dr in directions:
                cells = []
                valid = True
                cur_q, cur_r = q, r
                for _ in range(length):
                    if (
                            not field.is_valid_cell(cur_q, cur_r)
                            or field.get_cell(cur_q, cur_r).state != CellState.EMPTY
                    ):
                        valid = False
                        break
                    for nq, nr in field.get_neighbors(cur_q, cur_r):
                        neighbor = field.get_cell(nq, nr)
                        if neighbor and neighbor.state == CellState.SHIP:
                            valid = False
                            break
                    if not valid:
                        break
                    cells.append((cur_q, cur_r))
                    cur_q += dq
                    cur_r += dr
                if valid:
                    positions.append(cells)
        return positions

    def _remove_ship(self, field: Field, ship_cells):
        for ship in field.boards:
            if set(ship.coordinate) == set(ship_cells):
                field.boards.remove(ship)
                break
        for q, r in ship_cells:
            field.set_cell_state(q, r, CellState.EMPTY)
        for q, r in ship_cells:
            for nq, nr in field.get_neighbors(q, r):
                cell = field.get_cell(nq, nr)
                if cell and cell.state == CellState.BUFFER:
                    is_shared = False
                    for other_ship in field.boards:
                        if other_ship.coordinate != ship_cells:
                            for sq, sr in other_ship.coordinate:
                                if (nq, nr) in field.get_neighbors(sq, sr):
                                    is_shared = True
                                    break
                            if is_shared:
                                break
                    if not is_shared:
                        field.set_cell_state(nq, nr, CellState.EMPTY)

    def _autoSetBoard(self, field: Field, length: int) -> bool:
        max_attempts = 5000
        empty_cells = [
            (q, r)
            for (q, r), cell in field.cells.items()
            if cell.state == CellState.EMPTY
        ]
        if not empty_cells:
            return False

        for _ in range(max_attempts):
            if self.field_type == "classic":
                orientation = randint(0, 1)
                if orientation == 0:
                    if length > self.width:
                        continue
                    x1 = randint(0, self.width - length)
                    y1 = randint(0, self.height - 1)
                    x2 = x1 + length - 1
                    y2 = y1
                else:
                    if length > self.height:
                        continue
                    x1 = randint(0, self.width - 1)
                    y1 = randint(0, self.height - length)
                    x2 = x1
                    y2 = y1 + length - 1
            else:
                axis = randint(0, 2)
                q1, r1 = choice(empty_cells)
                if axis == 0:
                    q2 = q1 + length - 1
                    r2 = r1
                elif axis == 1:
                    q2 = q1 + length - 1
                    r2 = r1 + length - 1
                else:
                    q2 = q1 - (length - 1)
                    r2 = r1 + length - 1
                if not field.is_valid_cell(q2, r2):
                    continue

            if self.field_type == "classic":
                valid = True
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    for y in range(min(y1, y2), max(y1, y2) + 1):
                        if (
                                not field.is_valid_cell(x, y)
                                or field.get_cell(x, y).state != CellState.EMPTY
                        ):
                            valid = False
                            break
                    if not valid:
                        break
                if not valid:
                    continue
                cells = [
                    (x, y)
                    for x in range(min(x1, x2), max(x1, x2) + 1)
                    for y in range(min(y1, y2), max(y1, y2) + 1)
                ]
            else:
                dq = 0 if q2 == q1 else (1 if q2 > q1 else -1)
                dr = 0 if r2 == r1 else (1 if r2 > r1 else -1)
                q, r = q1, r1
                valid = True
                cells = []
                for _ in range(length):
                    if (
                            not field.is_valid_cell(q, r)
                            or field.get_cell(q, r).state != CellState.EMPTY
                    ):
                        valid = False
                        break
                    cells.append((q, r))
                    q += dq
                    r += dr
                if not valid:
                    continue

            for q, r in cells:
                field.set_cell_state(q, r, CellState.SHIP)
            self.setBufferAroundShip(field, cells)
            field.addBoard(cells)
            self.ship_counts[length] -= 1
            return True
        return False
