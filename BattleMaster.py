from SetBoard import *
from Field import *
from HitMaker import *

class BattleMaster:
    def __init__(self, width=10, height=10, ship_counts=None, bot_type="smart"):
        self.player_1 = Field(width, height)
        self.Bot_player = Field(width, height)
        self.shipPlacer = ShipPlacer(width, height, ship_counts)
        self.botPlacer = ShipPlacer(width, height, ship_counts)
        self.hitMaker = HitMaker()
        self.bot_type = bot_type
        if self.bot_type == "smart":
            self.hitMaker.initBotAI(self.player_1)

    def start(self):
        self.botPlacer.autoSetBoards(self.Bot_player)

    def putShip(self, x1: int, y1: int, x2: int = None, y2: int = None) -> bool:
        if x2 is None or y2 is None:
            x2, y2 = x1, y1
        return self.shipPlacer.setBoard(self.player_1, x1, y1, x2, y2)

    def howShips(self):
        return self.shipPlacer.howManyShips()

    def playerAttack(self, x: int, y: int) -> HitState:
        return self.hitMaker.hit(self.Bot_player, x, y)

    def botAttack(self) -> HitState:
        if self.bot_type == "smart":
            return self.hitMaker.smartHit(self.player_1)
        else:
            return self.hitMaker.randomHit(self.player_1)

    def fieldIsFilled(self):
        arr = self.howShips()
        for s in arr:
            if arr[s] != 0:
                return False
        return True

    def checkWin(self):
        if not self.Bot_player.hasLiveShips():
            return "player"
        if not self.player_1.hasLiveShips():
            return "bot"
        return None

    def watchMyField(self):
        return str(self.player_1)

    def watchOppField(self):
        return self.Bot_player.vragField()