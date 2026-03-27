import re

from BattleMaster import *


class SeaBattle:
    def __init__(self):
        self.bm = BattleMaster()
        self.is_player_turn = True
        self.fieldIsFilled = False

    def parse_input(self, user_input: str):
        user_input = user_input.strip().lower()
        # Ищем букву (a-j) и число (1-10)
        match = re.search(r'([a-j])', user_input)
        num_match = re.search(r'(\d+)', user_input)

        if not match or not num_match:
            return None, None

        letters = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8, 'j': 9}

        y = letters[match.group(1)]
        x = int(num_match.group(1)) - 1  # Вычитаем 1, чтобы 10 стала индексом 9

        # Проверка границ поля 10x10
        if 0 <= x <= 9:
            return x, y
        return None, None

    def commandOrganizer(self, user_input):
        user_input = user_input.strip().lower()

        if user_input == "/start":
            self.bm.start()
            return "Вводи координаты, куда хочешь поставить корабль (например, 'a1' или 'a1 a4'):"
        elif user_input == "/info":
            try:
                return open('rules.txt', 'r', encoding='utf-8').read()
            except:
                return "Правила игры: расставь корабли и стреляй по полю врага."
        elif user_input == "/cmf":
            return self.bm.watchMyField()
        elif user_input == "/cof":
            return self.bm.watchOppField()
        elif user_input == "/hs":
            return self.bm.howShips()

        elif not self.fieldIsFilled:
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

            return "Неверный ввод. Используй формат 'a10' или 'a1 a4'."

        elif self.fieldIsFilled:
            x, y = self.parse_input(user_input)
            if x is not None:
                hit = self.bm.playerAttack(x, y)
                if self.bm.checkWin() == "player":
                    return "Ты победил! Поздравляю!"
                if hit == HitState.ERR:
                    return "Ты уже стрелял в эту точку!z"
                elif hit == HitState.HIT:
                    return "Ты попал! Стреляй ещё!"
                elif hit == HitState.CRUSHED:
                    return "Ты вынес корабль! Стреляй ещё!"
                elif hit == HitState.MISS:
                    return "Промах! Эх... Повезет в следующий раз\n" + self.botHit()
            return "Неверные координаты для выстрела. Вводи от a1 до j10."

        return "Неверный ввод. Попробуй ещё раз!"

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
