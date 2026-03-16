from SetBoard import *
from Field import *
from HitMaker import *


class BattleMaster:
    def __init__(self):
        self.player_1 = Field()
        self.Bot_player = Field()
        self.shipPlacer = ShipPlacer()
        self.hitMaker = HitMaker()

    def start(self):
        ShipPlacer().autoSetBoards(self.Bot_player)

    def putShip(self, x1: int, y1: int, x2: int = None, y2: int = None) -> str:
        if x2 is None or y2 is None:
            x2 = x1
            y2 = y1
        if self.shipPlacer.setBoard(self.player_1, x1, y1, x2, y2):
            return (f"Супер {abs(x1 - x2) + 1 if abs(x1 - x2) > abs(y1 - y2) else abs(y1 - y2) + 1}"
                    f" палубный корабль поставлен!\nЖду следующие координаты)")
        return "Неверные координаты :( \nПопробуй ещё раз..."

    def howShips(self):
        mes = "Осталось:"
        for length, count in self.shipPlacer.howManyShips():
            mes += f"\n{count} - {length}-палубных кораблей"
        return mes

    def playerAttack(self, x, y):
        hitState: HitState = self.hitMaker.hit(self.Bot_player, x, y)
        if HitState.HIT == hitState:
            return "Ты попал!\nСтреляй ещё раз)"
        elif HitState.CRUSHED == hitState:
            return "Ты попал и убил КОРАБЛЬ!\nСтреляй ещё раз)"
        elif HitState.MISS == hitState:
            return "Промах(\nНичего страшного, повезет потом!"

    def botAttack(self):
        hitState: HitState = self.hitMaker.randomHit(self.player_1)
        if HitState.HIT == hitState:
            return "Бот попал!\nНу сейчас он точно промахнётся ;)"
        elif HitState.CRUSHED == hitState:
            return "О, чёрт! Бот попал и убил корабль :(\nРаз в год и палка стреляет >:("
        elif HitState.MISS == hitState:
            return "Бот промахнулся!\nСтреляй и покажи ему, кто на поле папочка!"
