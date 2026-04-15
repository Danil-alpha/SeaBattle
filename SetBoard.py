import re
from BattleMaster import *

class SeaBattle:
    def __init__(self):
        self.width = 10
        self.height = 10
        self.ship_counts = None
        self.bm = None
        self.is_player_turn = True
        self.fieldIsFilled = False
        self.game_started = False
        self.bot_type = "smart"

    def _build_letter_map(self):
        if self.width > 26:
            return {}
        return {chr(ord('a') + i): i for i in range(self.width)}

    def parse_input(self, user_input: str):
        user_input = user_input.strip().lower()
        letter_map = self._build_letter_map()
        if self.width > 26:
            parts = user_input.split()
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                y = int(parts[0]) - 1
                x = int(parts[1]) - 1
                if 0 <= x < self.width and 0 <= y < self.height:
                    return x, y
            return None, None
        else:
            match = re.search(r'([a-z])', user_input)
            num_match = re.search(r'(\d+)', user_input)
            if not match or not num_match:
                return None, None
            x = letter_map.get(match.group(1))
            if x is None:
                return None, None
            y = int(num_match.group(1)) - 1
            if 0 <= x < self.width and 0 <= y < self.height:
                return x, y
            return None, None

    def commandOrganizer(self, user_input):
        user_input = user_input.strip().lower()

        if not self.game_started:
            if user_input == "/set_width":
                return "Использование: /set_width <число от 1 до 26>"
            if user_input.startswith("/set_width "):
                try:
                    w = int(user_input.split()[1])
                    if 1 <= w <= 26:
                        self.width = w
                        return f"Ширина поля установлена на {self.width}. Текущая высота: {self.height}"
                    else:
                        return "Ширина должна быть от 1 до 26."
                except:
                    return "Неверный формат. Пример: /set_width 12"

            if user_input == "/set_height":
                return "Использование: /set_height <число от 1 до 26>"
            if user_input.startswith("/set_height "):
                try:
                    h = int(user_input.split()[1])
                    if 1 <= h <= 26:
                        self.height = h
                        return f"Высота поля установлена на {self.height}. Текущая ширина: {self.width}"
                    else:
                        return "Высота должна быть от 1 до 26."
                except:
                    return "Неверный формат. Пример: /set_height 12"

            if user_input == "/set_size":
                return "Использование: /set_size N (квадрат NxN) или /set_size N M (прямоугольник NxM)"
            if user_input.startswith("/set_size "):
                parts = user_input.split()[1:]
                try:
                    if len(parts) == 1:
                        n = int(parts[0])
                        if 1 <= n <= 26:
                            self.width = self.height = n
                            return f"Размер поля установлен на {n}x{n}"
                        else:
                            return "Размер должен быть от 1 до 26."
                    elif len(parts) == 2:
                        w = int(parts[0])
                        h = int(parts[1])
                        if 1 <= w <= 26 and 1 <= h <= 26:
                            self.width, self.height = w, h
                            return f"Размер поля установлен на {self.width}x{self.height}"
                        else:
                            return "Ширина и высота должны быть от 1 до 26."
                    else:
                        return "Неверный формат. Пример: /set_size 10 или /set_size 12 8"
                except:
                    return "Ошибка в числах."

            if user_input == "/set_ships":
                return "Использование: /set_ships длина1:количество1 длина2:количество2 ... (например /set_ships 4:1 3:2 2:3 1:4)"
            if user_input.startswith("/set_ships "):
                parts = user_input.split()[1:]
                new_counts = {}
                for part in parts:
                    if ':' not in part:
                        return "Неверный формат. Используй длина:количество, например 4:1"
                    length_str, cnt_str = part.split(':')
                    try:
                        length = int(length_str)
                        cnt = int(cnt_str)
                        if length <= 0 or cnt < 0:
                            return "Длина и количество должны быть положительными."
                        new_counts[length] = cnt
                    except:
                        return "Ошибка в числах."
                if not new_counts:
                    return "Не задано ни одного типа кораблей."
                self.ship_counts = new_counts
                return f"Набор кораблей установлен: {self.ship_counts}"

            if user_input == "/set_bot":
                return "Использование: /set_bot smart или /set_bot random"
            if user_input.startswith("/set_bot "):
                bot_choice = user_input.split()[1]
                if bot_choice in ("smart", "random"):
                    self.bot_type = bot_choice
                    return f"Тип бота установлен: {'умный' if bot_choice == 'smart' else 'случайный'}"
                else:
                    return "Неверный тип бота. Допустимые значения: smart, random"

        if user_input == "/start":
            if self.game_started:
                return "Игра уже начата. Используй /cmf, /cof, /hs или стреляй."
            self.bm = BattleMaster(width=self.width, height=self.height, ship_counts=self.ship_counts, bot_type=self.bot_type)
            self.bm.start()
            self.game_started = True
            return f"Игра началась на поле {self.width}x{self.height}!\nВводи координаты, куда хочешь поставить корабль (например, 'a1' или 'a1 a4'):"

        elif user_input == "/auto_set":
            if self.game_started:
                return "Игра уже начата, автоматическая расстановка невозможна."
            self.bm = BattleMaster(width=self.width, height=self.height, ship_counts=self.ship_counts, bot_type=self.bot_type)
            self.bm.start()  # расставляет бота
            self.bm.shipPlacer.autoSetBoards(self.bm.player_1)
            self.game_started = True
            self.fieldIsFilled = True
            return "Корабли расставлены автоматически! Игра началась. Можешь стрелять!"

        elif user_input == "/info":
            try:
                return open('rules.txt', 'r', encoding='utf-8').read()
            except:
                return "Правила игры: расставь корабли и стреляй по полю врага."

        elif user_input == "/cmf":
            if not self.game_started:
                return "Сначала начни игру командой /start или /auto_set"
            return self.bm.watchMyField()

        elif user_input == "/cof":
            if not self.game_started:
                return "Сначала начни игру командой /start или /auto_set"
            return self.bm.watchOppField()

        elif user_input == "/hs":
            if not self.game_started:
                return "Сначала начни игру командой /start или /auto_set"
            return self.bm.howShips()

        if not self.game_started:
            return "Игра не начата. Введи /start для ручной расстановки или /auto_set для автоматической, либо настрой параметры (/set_width, /set_height, /set_size, /set_ships, /set_bot)."

        if not self.fieldIsFilled:
            parts = user_input.split()
            if len(parts) == 1:
                x, y = self.parse_input(parts[0])
                if x is not None:
                    if not self.bm.putShip(x, y):
                        return "Сюда нельзя поставить корабль(("
                    if self.bm.fieldIsFilled():
                        self.fieldIsFilled = True
                        return "Все корабли поставлены! Можешь начинать стрелять!"
                    return "Корабль поставлен!"
            elif len(parts) == 2:
                x1, y1 = self.parse_input(parts[0])
                x2, y2 = self.parse_input(parts[1])
                if x1 is not None and x2 is not None:
                    if not self.bm.putShip(x1, y1, x2, y2):
                        return "Сюда нельзя поставить корабль(("
                    if self.bm.fieldIsFilled():
                        self.fieldIsFilled = True
                        return "Все корабли поставлены! Можешь начинать стрелять!"
                    return "Корабль поставлен!"
            return "Неверный ввод. Используй формат 'a1' или 'a1 a4'."

        x, y = self.parse_input(user_input)
        if x is not None:
            hit = self.bm.playerAttack(x, y)
            if self.bm.checkWin() == "player":
                return "Ты победил! Поздравляю!"
            if hit == HitState.ERR:
                return "Ты уже стрелял в эту точку!"
            elif hit == HitState.HIT:
                return "Ты попал! Стреляй ещё!"
            elif hit == HitState.CRUSHED:
                return "Ты вынес корабль! Стреляй ещё!"
            elif hit == HitState.MISS:
                return "Промах! Эх... Повезет в следующий раз\n" + self.botHit()
        return "Неверные координаты для выстрела."

    def botHit(self):
        hit = self.bm.botAttack()
        if self.bm.checkWin() == "bot":
            return "Бот победил!"
        if hit == HitState.HIT:
            return "Бот попал!\n" + self.botHit()
        elif hit == HitState.CRUSHED:
            return "Бот вынес твой корабль!\n" + self.botHit()
        elif hit == HitState.MISS:
            return "Бот промахнулся! Твой ход!"