import tkinter as tk
from tkinter import messagebox, ttk
import math
from battle_master import BattleMaster
from field import CellState, Field, Cell
from hit_maker import HitMaker, HitState


class SeaBattleGUI:
    def __init__(self, master):
        self.master = master
        master.title("Морской бой")
        master.resizable(False, False)

        self.radius = 3
        self.width = 10
        self.height = 10
        self.ship_counts = {4: 1, 3: 2, 2: 3, 1: 4}
        self.bot_type = "smart"
        self.field_type = "classic"
        self.game_mode = "vs_bot"

        self.bm = None
        self.game_started = False
        self.player_turn = True
        self.game_over = False
        self.current_player = 0
        self.placement_phase = 0

        self.cell_size = 30
        self.offset_x = 0
        self.offset_y = 0

        self.placement_mode = False
        self.pending_ship_start = None
        self.temp_ship_cells = []
        self.ships_placed = {}

        self.shot_processor = HitMaker()

        self.create_menu()
        self.create_control_panel()
        self.create_fields()

    def create_menu(self):
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        game_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Игра", menu=game_menu)
        game_menu.add_command(label="Новая игра", command=self.new_game)
        game_menu.add_command(label="Настройки", command=self.open_settings)
        game_menu.add_separator()
        game_menu.add_command(label="Выход", command=self.master.quit)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="Правила", command=self.show_rules)

    def create_control_panel(self):
        control_frame = tk.Frame(self.master)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self.status_label = tk.Label(
            control_frame,
            text="Добро пожаловать! Настройте игру и нажмите 'Новая игра'.",
            font=("Arial", 12),
        )
        self.status_label.pack(side=tk.LEFT, padx=10)

        self.reset_placement_btn = tk.Button(
            control_frame,
            text="Сбросить корабли",
            command=self.reset_player_ships,
            state=tk.DISABLED,
        )
        self.reset_placement_btn.pack(side=tk.RIGHT, padx=5)

        self.auto_set_btn = tk.Button(
            control_frame,
            text="Авто-расстановка",
            command=self.auto_place_ships,
            state=tk.DISABLED,
        )
        self.auto_set_btn.pack(side=tk.RIGHT, padx=5)

        self.start_btn = tk.Button(
            control_frame,
            text="Начать игру",
            command=self.start_game,
            state=tk.DISABLED,
        )
        self.start_btn.pack(side=tk.RIGHT, padx=5)

    def create_fields(self):
        main_frame = tk.Frame(self.master)
        main_frame.pack(padx=10, pady=10)

        self.player_frame = tk.LabelFrame(
            main_frame, text="Поле игрока 1", font=("Arial", 12, "bold")
        )
        self.player_frame.pack(side=tk.LEFT, padx=10)
        self.player_canvas = tk.Canvas(self.player_frame, bg="lightblue")
        self.player_canvas.pack()
        self.player_canvas.bind("<Button-1>", self.on_player_canvas_click)
        self.player_canvas.bind("<Motion>", self.on_player_canvas_motion)

        self.bot_frame = tk.LabelFrame(
            main_frame, text="Поле игрока 2", font=("Arial", 12, "bold")
        )
        self.bot_frame.pack(side=tk.RIGHT, padx=10)
        self.bot_canvas = tk.Canvas(self.bot_frame, bg="lightblue")
        self.bot_canvas.pack()
        self.bot_canvas.bind("<Button-1>", self.on_bot_canvas_click)
        self.bot_canvas.bind("<Motion>", self.on_bot_canvas_motion)

    def _hex_to_pixel(self, q, r):
        size = self.cell_size
        x = size * (math.sqrt(3) * q + math.sqrt(3) / 2 * r)
        y = size * (3.0 / 2 * r)
        return self.offset_x + x, self.offset_y + y

    def _pixel_to_hex(self, px, py):
        size = self.cell_size
        px -= self.offset_x
        py -= self.offset_y
        q = (math.sqrt(3) / 3 * px - 1.0 / 3 * py) / size
        r = (2.0 / 3 * py) / size
        return self._hex_round(q, r)

    def _hex_round(self, q, r):
        s = -q - r
        rq = round(q)
        rr = round(r)
        rs = round(s)
        q_diff = abs(rq - q)
        r_diff = abs(rr - r)
        s_diff = abs(rs - s)
        if q_diff > r_diff and q_diff > s_diff:
            rq = -rr - rs
        elif r_diff > s_diff:
            rr = -rq - rs
        return rq, rr

    def _hex_vertices(self, cx, cy):
        size = self.cell_size
        vertices = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.radians(angle_deg)
            x = cx + size * math.cos(angle_rad)
            y = cy + size * math.sin(angle_rad)
            vertices.append((x, y))
        return vertices

    def _draw_hex(self, canvas, q, r, fill_color, outline="black", tags=()):
        cx, cy = self._hex_to_pixel(q, r)
        vertices = self._hex_vertices(cx, cy)
        canvas.create_polygon(vertices, fill=fill_color, outline=outline, tags=tags)

    def _compute_offsets(self, canvas, cells):
        if not cells:
            return
        min_x = min_y = float("inf")
        max_x = max_y = -float("inf")
        old_ox, old_oy = self.offset_x, self.offset_y
        self.offset_x = self.offset_y = 0
        for q, r in cells:
            cx, cy = self._hex_to_pixel(q, r)
            min_x = min(min_x, cx - self.cell_size)
            max_x = max(max_x, cx + self.cell_size)
            min_y = min(min_y, cy - self.cell_size)
            max_y = max(max_y, cy + self.cell_size)
        self.offset_x, self.offset_y = old_ox, old_oy

        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        if canvas_width <= 1:
            canvas_width = canvas.winfo_reqwidth()
            canvas_height = canvas.winfo_reqheight()
        if canvas_width <= 1:
            canvas_width = 600
            canvas_height = 600

        self.offset_x = (canvas_width - (max_x - min_x)) / 2 - min_x
        self.offset_y = (canvas_height - (max_y - min_y)) / 2 - min_y

    def _set_canvas_fixed_size(self):
        if self.field_type == "classic":
            width = self.width * self.cell_size + 50
            height = self.height * self.cell_size + 50
        else:
            size = self.cell_size
            max_q = self.radius
            max_r = self.radius
            min_x = min_y = float("inf")
            max_x = max_y = -float("inf")
            old_ox, old_oy = self.offset_x, self.offset_y
            self.offset_x = self.offset_y = 0
            for q in range(-max_q, max_q + 1):
                r1 = max(-max_r, -q - max_r)
                r2 = min(max_r, -q + max_r)
                for r in range(r1, r2 + 1):
                    cx, cy = self._hex_to_pixel(q, r)
                    min_x = min(min_x, cx - size)
                    max_x = max(max_x, cx + size)
                    min_y = min(min_y, cy - size)
                    max_y = max(max_y, cy + size)
            self.offset_x, self.offset_y = old_ox, old_oy
            width = int(max_x - min_x) + 40
            height = int(max_y - min_y) + 40
        self.player_canvas.config(width=width, height=height)
        self.bot_canvas.config(width=width, height=height)

    def update_fields_display(self):
        if not self.bm:
            return

        self.master.update_idletasks()

        if self.field_type == "hex":
            self._compute_offsets(self.player_canvas, self.bm.player_field.cells.keys())
        else:
            self.offset_x = 30
            self.offset_y = 30

        self.player_canvas.delete("cell")
        self.player_canvas.delete("temp_ship")
        self.bot_canvas.delete("cell")
        self.bot_canvas.delete("temp_ship")

        if self.game_started:
            if self.game_mode == "vs_human":
                show_player1_ships = False
                show_player2_ships = False
                if self.current_player == 0:
                    self.player_frame.config(text="Поле игрока 1 (ваш ход)")
                    self.bot_frame.config(text="Поле игрока 2")
                else:
                    self.player_frame.config(text="Поле игрока 1")
                    self.bot_frame.config(text="Поле игрока 2 (ваш ход)")
            else:
                show_player1_ships = True
                show_player2_ships = False
        else:
            show_player1_ships = self.placement_phase == 0
            show_player2_ships = self.placement_phase == 1

        for (q, r), cell in self.bm.player_field.cells.items():
            self._draw_cell(
                self.player_canvas, q, r, cell.state, show_ships=show_player1_ships
            )

        for (q, r), cell in self.bm.bot_field.cells.items():
            self._draw_cell(
                self.bot_canvas, q, r, cell.state, show_ships=show_player2_ships
            )

        if self.placement_mode and self.temp_ship_cells:
            if self.game_mode != "vs_human" or self.placement_phase == 0:
                canvas = self.player_canvas
                field = self.bm.player_field
            else:
                canvas = self.bot_canvas
                field = self.bm.bot_field
            for q, r in self.temp_ship_cells:
                if field.is_valid_cell(q, r):
                    if self.field_type == "classic":
                        x1 = self.offset_x + q * self.cell_size
                        y1 = self.offset_y + r * self.cell_size
                        x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                        canvas.create_rectangle(
                            x1,
                            y1,
                            x2,
                            y2,
                            fill="lightgreen",
                            outline="green",
                            tags="temp_ship",
                        )
                    else:
                        self._draw_hex(
                            canvas,
                            q,
                            r,
                            "lightgreen",
                            outline="green",
                            tags="temp_ship",
                        )

    def _draw_cell(self, canvas, q, r, state, show_ships):
        if show_ships:
            colors = {
                CellState.EMPTY: "white",
                CellState.SHIP: "gray",
                CellState.BUFFER: "#A9A9A9",
                CellState.HIT: "red",
                CellState.MISS: "blue",
            }
            fill_color = colors.get(state, "white")
        else:
            if state in (CellState.HIT, CellState.MISS):
                colors = {CellState.HIT: "red", CellState.MISS: "blue"}
                fill_color = colors.get(state, "white")
            else:
                fill_color = "white"

        if self.field_type == "classic":
            x1 = self.offset_x + q * self.cell_size
            y1 = self.offset_y + r * self.cell_size
            x2, y2 = x1 + self.cell_size, y1 + self.cell_size
            canvas.create_rectangle(
                x1, y1, x2, y2, fill=fill_color, outline="black", tags="cell"
            )
        else:
            self._draw_hex(canvas, q, r, fill_color, outline="black", tags="cell")

    def _get_ship_cells_between(self, start, end):
        if self.field_type == "classic":
            x1, y1 = start
            x2, y2 = end
            if x1 == x2:
                step_y = 1 if y2 > y1 else -1
                return [(x1, y) for y in range(y1, y2 + step_y, step_y)]
            elif y1 == y2:
                step_x = 1 if x2 > x1 else -1
                return [(x, y1) for x in range(x1, x2 + step_x, step_x)]
            else:
                return []
        else:
            q1, r1 = start
            q2, r2 = end
            dq = q2 - q1
            dr = r2 - r1
            if not (dr == 0 or dq == 0 or dq == -dr):
                return []
            length = max(abs(dq), abs(dr)) + 1
            step_q = 0 if dq == 0 else (1 if dq > 0 else -1)
            step_r = 0 if dr == 0 else (1 if dr > 0 else -1)
            cells = []
            q, r = q1, r1
            for _ in range(length):
                cells.append((q, r))
                q += step_q
                r += step_r
            return cells

    def _can_place_ship(self, cells, field):
        if not cells:
            return False
        for q, r in cells:
            if not field.is_valid_cell(q, r):
                return False
            cell = field.get_cell(q, r)
            if cell.state != CellState.EMPTY:
                return False
        for q, r in cells:
            for nq, nr in field.get_neighbors(q, r):
                neighbor = field.get_cell(nq, nr)
                if neighbor and neighbor.state == CellState.SHIP:
                    return False
        return True

    def _update_ship_counts_display(self):
        if not self.placement_mode:
            return
        remaining = []
        for length in sorted(self.ships_placed.keys(), reverse=True):
            if self.ships_placed[length] > 0:
                remaining.append(f"{length}:{self.ships_placed[length]}")
        if remaining:
            text = "Расставьте корабли. Осталось: " + ", ".join(remaining)
        else:
            text = "Все корабли расставлены! Нажмите 'Начать игру'."
        self.status_label.config(text=text)

    def _place_ship(self, cells, field, placer):
        if not cells:
            return False
        length = len(cells)
        if length not in self.ships_placed or self.ships_placed[length] <= 0:
            messagebox.showinfo(
                "Ошибка", f"Корабль длины {length} больше не требуется."
            )
            return False

        if not self._can_place_ship(cells, field):
            buffer_found = False
            for q, r in cells:
                cell = field.get_cell(q, r)
                if cell and cell.state == CellState.BUFFER:
                    buffer_found = True
                    break
            if buffer_found:
                messagebox.showinfo(
                    "Ошибка",
                    "Одна из выбранных клеток находится рядом с уже поставленным кораблём (буферная зона).\n"
                    "Корабли не могут касаться друг друга даже углами.",
                )
            else:
                messagebox.showinfo(
                    "Ошибка",
                    "Невозможно разместить корабль здесь (пересечение или касание).",
                )
            return False

        q1, r1 = cells[0]
        q2, r2 = cells[-1]
        success = placer.setBoard(field, q1, r1, q2, r2)
        if success:
            self.ships_placed[length] -= 1
            self._update_ship_counts_display()
            self.temp_ship_cells = []
            self.pending_ship_start = None
            self.update_fields_display()
            return True
        else:
            messagebox.showinfo("Ошибка", "Не удалось разместить корабль.")
            return False

    def reset_player_ships(self):
        if not self.bm:
            return
        if self.game_mode == "vs_human":
            if self.placement_phase == 0:
                self.bm.player_field = Field(
                    radius=self.radius,
                    field_type=self.field_type,
                    width=self.width,
                    height=self.height,
                )
                self.bm.player_placer.ship_counts = (
                    self.bm.player_placer.original_counts.copy()
                )
                self.ships_placed = self.bm.player_placer.original_counts.copy()
            else:
                self.bm.bot_field = Field(
                    radius=self.radius,
                    field_type=self.field_type,
                    width=self.width,
                    height=self.height,
                )
                self.bm.bot_placer.ship_counts = (
                    self.bm.bot_placer.original_counts.copy()
                )
                self.ships_placed = self.bm.bot_placer.original_counts.copy()
        else:
            self.bm.player_field = Field(
                radius=self.radius,
                field_type=self.field_type,
                width=self.width,
                height=self.height,
            )
            self.ships_placed = self.bm.player_placer.original_counts.copy()

        self.placement_mode = True
        self.pending_ship_start = None
        self.temp_ship_cells = []
        self.start_btn.config(state=tk.DISABLED)
        self.auto_set_btn.config(state=tk.NORMAL)
        self.reset_placement_btn.config(state=tk.NORMAL)
        self._update_ship_counts_display()
        self.update_fields_display()

    def _start_placement_mode(self):
        self.placement_mode = True
        self.ships_placed = self.bm.player_placer.original_counts.copy()
        self.pending_ship_start = None
        self.temp_ship_cells = []
        self.start_btn.config(state=tk.DISABLED)
        self.auto_set_btn.config(state=tk.NORMAL)
        self.reset_placement_btn.config(state=tk.NORMAL)
        self._update_ship_counts_display()
        self.update_fields_display()

    def _start_placement_for_player(self, player_index):
        self.placement_mode = True
        self.placement_phase = player_index
        if player_index == 0:
            self.ships_placed = self.bm.player_placer.original_counts.copy()
            self.player_frame.config(text="Поле игрока 1 (расстановка)")
            self.bot_frame.config(text="Поле игрока 2 (скрыто)")
        else:
            self.ships_placed = self.bm.bot_placer.original_counts.copy()
            self.player_frame.config(text="Поле игрока 1 (скрыто)")
            self.bot_frame.config(text="Поле игрока 2 (расстановка)")
        self.pending_ship_start = None
        self.temp_ship_cells = []
        self.start_btn.config(state=tk.DISABLED)
        self.auto_set_btn.config(state=tk.NORMAL)
        self.reset_placement_btn.config(state=tk.NORMAL)
        self.update_fields_display()

    def on_player_canvas_click(self, event):
        if self.game_started:
            if self.game_mode == "vs_human":
                if self.current_player == 1 and not self.game_over:
                    self._handle_shot(event, target_is_player2=False)
            return

        if not self.placement_mode:
            return
        if self.game_mode == "vs_human" and self.placement_phase != 0:
            return
        field = self.bm.player_field
        placer = self.bm.player_placer
        self._handle_placement_click(event, field, placer)

    def on_bot_canvas_click(self, event):
        if self.game_started:
            if self.game_mode == "vs_human":
                if self.current_player == 0 and not self.game_over:
                    self._handle_shot(event, target_is_player2=True)
                return
            else:
                if not self.player_turn or self.game_over:
                    return
                self._handle_bot_shot(event)
                return

        if not self.placement_mode:
            return
        if self.game_mode == "vs_human" and self.placement_phase != 1:
            return
        field = self.bm.bot_field
        placer = self.bm.bot_placer
        self._handle_placement_click(event, field, placer)

    def _handle_bot_shot(self, event):
        target_field = self.bm.bot_field

        if self.field_type == "classic":
            x = (event.x - self.offset_x) // self.cell_size
            y = (event.y - self.offset_y) // self.cell_size
            if not target_field.is_valid_cell(x, y):
                return
            q, r = x, y
        else:
            q, r = self._pixel_to_hex(event.x, event.y)
            if not target_field.is_valid_cell(q, r):
                return

        cell = target_field.get_cell(q, r)
        if cell.state in (CellState.HIT, CellState.MISS):
            self.status_label.config(text="Клетка уже обстреляна!")
            return

        result = self.bm.player_attack(q, r)
        self.update_fields_display()

        if result == HitState.MISS:
            self.status_label.config(text="Промах! Ход бота.")
            self.player_turn = False
            self.master.after(500, self.bot_turn)
        elif result == HitState.HIT:
            self.status_label.config(text="Попадание! Стреляйте ещё.")
        elif result == HitState.CRUSHED:
            self.status_label.config(text="Корабль уничтожен! Стреляйте ещё.")

        if self.bm.check_winner() == "player":
            self.game_over = True
            self.status_label.config(text="Поздравляем! Вы победили!")
            messagebox.showinfo("Победа", "Вы потопили все корабли противника!")
        self.update_fields_display()

    def _handle_shot(self, event, target_is_player2):
        if target_is_player2:
            target_field = self.bm.bot_field
        else:
            target_field = self.bm.player_field

        if self.field_type == "classic":
            x = (event.x - self.offset_x) // self.cell_size
            y = (event.y - self.offset_y) // self.cell_size
            if not target_field.is_valid_cell(x, y):
                return
            q, r = x, y
        else:
            q, r = self._pixel_to_hex(event.x, event.y)
            if not target_field.is_valid_cell(q, r):
                return

        cell = target_field.get_cell(q, r)
        if cell.state in (CellState.HIT, CellState.MISS):
            self.status_label.config(text="Клетка уже обстреляна!")
            return

        result = self.shot_processor.hit(target_field, q, r)
        self.update_fields_display()

        if result == HitState.MISS:
            self.status_label.config(
                text=f"Промах! Ход игрока {2 - self.current_player}"
            )
            self.current_player = 1 - self.current_player
            if self.current_player == 0:
                self.player_frame.config(text="Поле игрока 1 (ваш ход)")
                self.bot_frame.config(text="Поле игрока 2 (ход противника)")
            else:
                self.player_frame.config(text="Поле игрока 1 (ход противника)")
                self.bot_frame.config(text="Поле игрока 2 (ваш ход)")
        elif result == HitState.HIT:
            self.status_label.config(
                text=f"Попадание! Игрок {self.current_player + 1} стреляет ещё."
            )
        elif result == HitState.CRUSHED:
            self.status_label.config(
                text=f"Корабль уничтожен! Игрок {self.current_player + 1} стреляет ещё."
            )

        if not self.bm.bot_field.hasLiveShips():
            self.game_over = True
            self.status_label.config(text="Игрок 1 победил!")
            messagebox.showinfo("Победа", "Игрок 1 потопил все корабли противника!")
        elif not self.bm.player_field.hasLiveShips():
            self.game_over = True
            self.status_label.config(text="Игрок 2 победил!")
            messagebox.showinfo("Победа", "Игрок 2 потопил все корабли противника!")
        self.update_fields_display()

    def _handle_placement_click(self, event, field, placer):
        if self.field_type == "classic":
            x = (event.x - self.offset_x) // self.cell_size
            y = (event.y - self.offset_y) // self.cell_size
            if not field.is_valid_cell(x, y):
                return
            coord = (x, y)
        else:
            coord = self._pixel_to_hex(event.x, event.y)
            if not field.is_valid_cell(*coord):
                return

        if self.pending_ship_start is None:
            self.pending_ship_start = coord
            self.temp_ship_cells = [coord]
            self.update_fields_display()
        else:
            cells = self._get_ship_cells_between(self.pending_ship_start, coord)
            if not cells:
                messagebox.showinfo("Ошибка", "Корабль должен быть прямой линией.")
                self.pending_ship_start = None
                self.temp_ship_cells = []
                self.update_fields_display()
                return

            length = len(cells)
            if length not in self.ships_placed or self.ships_placed[length] <= 0:
                messagebox.showinfo("Ошибка", f"Нет доступных кораблей длины {length}.")
                self.pending_ship_start = None
                self.temp_ship_cells = []
                self.update_fields_display()
                return

            if self._place_ship(cells, field, placer):
                if self.game_mode == "vs_human":
                    if self.placement_phase == 0 and self.bm.player_ships_placed():
                        self.placement_phase = 1
                        self._start_placement_for_player(1)
                    elif self.placement_phase == 1 and self.bm.bot_ships_placed():
                        self.placement_mode = False
                        self.start_btn.config(state=tk.NORMAL)
                        self.auto_set_btn.config(state=tk.DISABLED)
                        self.reset_placement_btn.config(state=tk.DISABLED)
                        self.status_label.config(
                            text="Все корабли расставлены! Нажмите 'Начать игру'."
                        )
                else:
                    if self.bm.player_ships_placed():
                        self.placement_mode = False
                        self.start_btn.config(state=tk.NORMAL)
                        self.auto_set_btn.config(state=tk.DISABLED)
                        self.reset_placement_btn.config(state=tk.DISABLED)
                        self.status_label.config(
                            text="Все корабли расставлены! Нажмите 'Начать игру'."
                        )

    def on_player_canvas_motion(self, event):
        if not self.placement_mode or self.pending_ship_start is None:
            return
        if self.game_mode == "vs_human" and self.placement_phase != 0:
            return
        field = self.bm.player_field
        self._handle_placement_motion(event, field)

    def on_bot_canvas_motion(self, event):
        if not self.placement_mode or self.pending_ship_start is None:
            return
        if self.game_mode == "vs_human" and self.placement_phase != 1:
            return
        field = self.bm.bot_field
        self._handle_placement_motion(event, field)

    def _handle_placement_motion(self, event, field):
        if self.field_type == "classic":
            x = (event.x - self.offset_x) // self.cell_size
            y = (event.y - self.offset_y) // self.cell_size
            if not field.is_valid_cell(x, y):
                return
            end_coord = (x, y)
        else:
            end_coord = self._pixel_to_hex(event.x, event.y)
            if not field.is_valid_cell(*end_coord):
                return

        cells = self._get_ship_cells_between(self.pending_ship_start, end_coord)
        if cells:
            max_len = max(self.ships_placed.keys()) if self.ships_placed else 0
            if len(cells) <= max_len:
                self.temp_ship_cells = cells
                self.update_fields_display()

    def bot_turn(self):
        if self.game_over:
            return
        result = self.bm.bot_attack()
        self.update_fields_display()

        if result == HitState.MISS:
            self.status_label.config(text="Бот промахнулся. Ваш ход.")
            self.player_turn = True
        elif result == HitState.HIT:
            self.status_label.config(text="Бот попал! Ходит снова...")
            self.master.after(500, self.bot_turn)
        elif result == HitState.CRUSHED:
            self.status_label.config(text="Бот уничтожил ваш корабль! Ходит снова...")
            self.master.after(500, self.bot_turn)

        if self.bm.check_winner() == "bot":
            self.game_over = True
            self.status_label.config(text="Бот победил...")
            messagebox.showinfo("Поражение", "Все ваши корабли потоплены.")
        self.update_fields_display()

    def new_game(self):
        self.game_started = False
        self.game_over = False
        self.player_turn = True
        self.current_player = 0
        self.placement_phase = 0
        self.placement_mode = True
        self.pending_ship_start = None
        self.temp_ship_cells = []

        try:
            self.bm = BattleMaster(
                field_type=self.field_type,
                radius=self.radius,
                width=self.width,
                height=self.height,
                ship_counts=self.ship_counts,
                bot_type=self.bot_type,
            )
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать игру: {e}")
            return

        self._set_canvas_fixed_size()
        if self.game_mode == "vs_human":
            self.placement_phase = 0
            self.player_frame.config(text="Поле игрока 1 (расстановка)")
            self.bot_frame.config(text="Поле игрока 2 (скрыто)")
            self._start_placement_for_player(0)
        else:
            self.player_frame.config(text="Ваше поле")
            self.bot_frame.config(text="Поле противника")
            self._start_placement_mode()

    def auto_place_ships(self):
        if not self.bm:
            return
        if self.game_mode == "vs_human":
            if self.placement_phase == 0:
                field = self.bm.player_field
                placer = self.bm.player_placer
            else:
                field = self.bm.bot_field
                placer = self.bm.bot_placer
            field.cells.clear()
            if self.field_type == "classic":
                for x in range(self.width):
                    for y in range(self.height):
                        field.cells[(x, y)] = Cell(x, y)
            else:
                for q in range(-self.radius, self.radius + 1):
                    r1 = max(-self.radius, -q - self.radius)
                    r2 = min(self.radius, -q + self.radius)
                    for r in range(r1, r2 + 1):
                        field.cells[(q, r)] = Cell(q, r)
            placer.ship_counts = placer.original_counts.copy()
            self.ships_placed = placer.original_counts.copy()
            self.update_fields_display()
        else:
            self.bm.player_field = Field(
                radius=self.radius,
                field_type=self.field_type,
                width=self.width,
                height=self.height,
            )
            self.bm.player_placer.ship_counts = (
                self.bm.player_placer.original_counts.copy()
            )
            self.temp_ship_cells = []
            self.pending_ship_start = None
            self.update_fields_display()

        try:
            if self.game_mode == "vs_human":
                success = placer.autoSetBoards(field)
            else:
                success = self.bm.player_placer.autoSetBoards(self.bm.player_field)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось расставить корабли: {e}")
            return

        if not success:
            messagebox.showerror(
                "Ошибка",
                "Не удалось разместить все корабли. Попробуйте"
                " увеличить радиус или уменьшить количество кораблей.",
            )
            return

        if self.game_mode == "vs_human":
            if not field.hasLiveShips():
                messagebox.showerror("Ошибка", "Не удалось расставить корабли.")
                return
            if self.placement_phase == 0:
                self.placement_phase = 1
                self._start_placement_for_player(1)
            else:
                self.placement_mode = False
                self.start_btn.config(state=tk.NORMAL)
                self.auto_set_btn.config(state=tk.DISABLED)
                self.reset_placement_btn.config(state=tk.DISABLED)
                self.status_label.config(
                    text="Корабли расставлены! Нажмите 'Начать игру'."
                )
        else:
            if not self.bm.player_field.hasLiveShips():
                messagebox.showerror("Ошибка", "Не удалось расставить ваши корабли.")
                return
            self.ships_placed = self.bm.player_placer.howManyShips().copy()
            self.placement_mode = False
            self.start_btn.config(state=tk.NORMAL)
            self.auto_set_btn.config(state=tk.DISABLED)
            self.reset_placement_btn.config(state=tk.DISABLED)
            self.status_label.config(
                text="Корабли расставлены автоматически! Нажмите 'Начать игру'."
            )
        self.update_fields_display()

    def start_game(self):
        if not self.bm:
            return
        if self.game_mode == "vs_bot":
            if not self.bm.player_ships_placed():
                messagebox.showinfo(
                    "Ошибка", "Расставьте все корабли перед началом игры."
                )
                return
            try:
                self.bm.start()
            except Exception as e:
                messagebox.showerror(
                    "Ошибка", f"Не удалось расставить корабли бота: {e}"
                )
                return
            if not self.bm.bot_field.hasLiveShips():
                messagebox.showerror("Ошибка", "Боту не удалось расставить корабли.")
                return
            self.placement_mode = False
            self.game_started = True
            self.start_btn.config(state=tk.DISABLED)
            self.auto_set_btn.config(state=tk.DISABLED)
            self.reset_placement_btn.config(state=tk.DISABLED)
            self.status_label.config(text="Игра началась! Ваш ход.")
        else:
            if not (self.bm.player_ships_placed() and self.bm.bot_ships_placed()):
                messagebox.showinfo("Ошибка", "Расставьте корабли обоих игроков.")
                return
            self.placement_mode = False
            self.game_started = True
            self.current_player = 0
            self.player_frame.config(text="Поле игрока 1 (ваш ход)")
            self.bot_frame.config(text="Поле игрока 2 (ход противника)")
            self.status_label.config(
                text="Игра началась! Ход игрока 1. Стреляйте по правому полю."
            )
        self.update_fields_display()

    def open_settings(self):
        settings_win = tk.Toplevel(self.master)
        settings_win.title("Настройки игры")
        settings_win.grab_set()

        row_idx = 0

        tk.Label(settings_win, text="Тип поля:").grid(
            row=row_idx, column=0, padx=5, pady=5, sticky="e"
        )
        field_combo = ttk.Combobox(
            settings_win, values=["classic", "hex"], state="readonly"
        )
        field_combo.set(self.field_type)
        field_combo.grid(row=row_idx, column=1, padx=5, pady=5)
        row_idx += 1

        size_frame = tk.Frame(settings_win)
        size_frame.grid(row=row_idx, column=0, columnspan=2, pady=5)
        row_idx += 1

        def update_size_widgets(*args):
            for w in size_frame.winfo_children():
                w.destroy()
            if field_combo.get() == "classic":
                tk.Label(size_frame, text="Ширина:").grid(
                    row=0, column=0, padx=5, pady=2
                )
                w_entry = tk.Entry(size_frame, width=5)
                w_entry.insert(0, str(self.width))
                w_entry.grid(row=0, column=1, padx=5, pady=2)
                tk.Label(size_frame, text="Высота:").grid(
                    row=1, column=0, padx=5, pady=2
                )
                h_entry = tk.Entry(size_frame, width=5)
                h_entry.insert(0, str(self.height))
                h_entry.grid(row=1, column=1, padx=5, pady=2)
                size_frame.w_entry = w_entry
                size_frame.h_entry = h_entry
            else:
                tk.Label(size_frame, text="Радиус:").grid(
                    row=0, column=0, padx=5, pady=2
                )
                r_entry = tk.Entry(size_frame, width=5)
                r_entry.insert(0, str(self.radius))
                r_entry.grid(row=0, column=1, padx=5, pady=2)
                size_frame.r_entry = r_entry

        field_combo.bind("<<ComboboxSelected>>", update_size_widgets)
        update_size_widgets()

        tk.Label(settings_win, text="Тип бота:").grid(
            row=row_idx, column=0, padx=5, pady=5, sticky="e"
        )
        bot_combo = ttk.Combobox(
            settings_win, values=["smart", "random"], state="readonly"
        )
        bot_combo.set(self.bot_type)
        bot_combo.grid(row=row_idx, column=1, padx=5, pady=5)
        row_idx += 1

        tk.Label(settings_win, text="Режим игры:").grid(
            row=row_idx, column=0, padx=5, pady=5, sticky="e"
        )
        mode_combo = ttk.Combobox(
            settings_win, values=["vs_bot", "vs_human"], state="readonly"
        )
        mode_combo.set(self.game_mode)
        mode_combo.grid(row=row_idx, column=1, padx=5, pady=5)
        row_idx += 1

        tk.Label(settings_win, text="Корабли (длина:кол-во):").grid(
            row=row_idx, column=0, padx=5, pady=5, sticky="e"
        )
        ships_entry = tk.Entry(settings_win, width=30)
        ships_str = " ".join(
            [f"{k}:{v}" for k, v in sorted(self.ship_counts.items(), reverse=True)]
        )
        ships_entry.insert(0, ships_str)
        ships_entry.grid(row=row_idx, column=1, padx=5, pady=5)
        row_idx += 1

        def save_settings():
            try:
                self.field_type = field_combo.get()
                if self.field_type == "classic":
                    self.width = int(size_frame.w_entry.get())
                    self.height = int(size_frame.h_entry.get())
                    self.radius = None
                else:
                    self.radius = int(size_frame.r_entry.get())
                    self.width = self.height = None
                self.bot_type = bot_combo.get()
                self.game_mode = mode_combo.get()
                parts = ships_entry.get().split()
                new_counts = {}
                for part in parts:
                    if ":" not in part:
                        raise ValueError
                    l_str, c_str = part.split(":")
                    length = int(l_str)
                    count = int(c_str)
                    if length <= 0 or count < 0:
                        raise ValueError
                    new_counts[length] = count
                if not new_counts:
                    raise ValueError
                self.ship_counts = new_counts
                settings_win.destroy()
                self.new_game()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Проверьте данные: {e}")

        tk.Button(settings_win, text="Сохранить", command=save_settings).grid(
            row=row_idx, column=0, columnspan=2, pady=10
        )

    def show_rules(self):

        with open("rules.txt", "r", encoding="utf-8") as f:
            rules = f.read()


if __name__ == "__main__":
    root = tk.Tk()
    app = SeaBattleGUI(root)
    root.mainloop()
