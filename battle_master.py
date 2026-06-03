from ship_placer import ShipPlacer
from hit_maker import HitMaker, HitState
from bot import Bot
from field import *


class BattleMaster:
    def __init__(self, field_type="classic", radius=3, width=10, height=10, ship_counts=None, bot_type="smart"):
        self.field_type = field_type
        self.radius = radius
        self.width = width
        self.height = height
        self.player_field = Field(
            radius=radius, field_type=field_type, width=width, height=height
        )
        self.bot_field = Field(
            radius=radius, field_type=field_type, width=width, height=height
        )
        self.player_placer = ShipPlacer(field_type, radius, width, height, ship_counts)
        self.bot_placer = ShipPlacer(field_type, radius, width, height, ship_counts)
        self.shot_processor = HitMaker()
        self.bot = Bot(bot_type)
        self.bot.set_enemy_field(self.player_field)

    def start(self):
        return self.bot_placer.autoSetBoards(self.bot_field)

    def put_ship(self, q1, r1, q2=None, r2=None):
        if q2 is None or r2 is None:
            q2, r2 = q1, r1
        return self.player_placer.setBoard(self.player_field, q1, r1, q2, r2)

    def how_many_ships_left(self):
        return self.player_placer.howManyShips()

    def player_attack(self, q, r):
        return self.shot_processor.hit(self.bot_field, q, r)

    def bot_attack(self):
        coords = self.bot.make_move()
        if coords is None:
            return HitState.ERR
        q, r = coords
        result = self.shot_processor.hit(self.player_field, q, r)
        self.bot.update(q, r, result)
        return result

    def player_ships_placed(self):
        arr = self.how_many_ships_left()
        for s in arr:
            if arr[s] != 0:
                return False
        return True

    def check_winner(self):
        if not self.bot_field.hasLiveShips():
            return "player"
        if not self.player_field.hasLiveShips():
            return "bot"
        return None

    def watch_my_field(self):
        return f"Поле игрока: {len(self.player_field.cells)} клеток"

    def watch_opp_field(self):
        return f"Поле бота: {len(self.bot_field.cells)} клеток"

    def bot_ships_placed(self):
        arr = self.bot_placer.howManyShips()
        for s in arr:
            if arr[s] != 0:
                return False
        return True
