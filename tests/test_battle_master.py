# tests/test_battle_master.py
import pytest
from battle_master import BattleMaster
from hit_maker import HitState
from field import CellState


class TestBattleMasterIntegration:
    def test_init(self):
        bm = BattleMaster(field_type="classic", width=8, height=8, bot_type="random")
        assert bm.player_field is not None
        assert bm.bot_field is not None
        assert bm.player_placer is not None
        assert bm.bot_placer is not None
        assert bm.bot.bot_type == "random"

    def test_start_places_bot_ships(self, battlemaster_classic):
        result = battlemaster_classic.start()
        assert result is True
        assert battlemaster_classic.bot_field.hasLiveShips() is True

    def test_put_ship_valid(self, battlemaster_classic):
        result = battlemaster_classic.put_ship(0, 0, 0, 2)
        assert result is True
        assert battlemaster_classic.player_field.get_cell(0, 1).state == CellState.SHIP

    def test_put_ship_invalid(self, battlemaster_classic):
        result = battlemaster_classic.put_ship(0, 0, 2, 2)
        assert result is False

    def test_player_ships_placed(self, battlemaster_classic):
        assert battlemaster_classic.player_ships_placed() is False
        success = battlemaster_classic.player_placer.autoSetBoards(
            battlemaster_classic.player_field
        )
        assert success is True
        total_ships = len(battlemaster_classic.player_field.boards)
        expected_total = sum(
            battlemaster_classic.player_placer.original_counts.values()
        )
        assert total_ships == expected_total
        assert battlemaster_classic.player_ships_placed() is True

    def test_player_attack(self, battlemaster_classic):
        battlemaster_classic.start()
        result = battlemaster_classic.player_attack(0, 0)
        assert result in (HitState.MISS, HitState.HIT, HitState.CRUSHED)

    def test_bot_attack(self, battlemaster_classic):
        battlemaster_classic.player_placer.autoSetBoards(
            battlemaster_classic.player_field
        )
        battlemaster_classic.start()
        result = battlemaster_classic.bot_attack()
        assert result in (HitState.MISS, HitState.HIT, HitState.CRUSHED, HitState.ERR)

    def test_check_winner_no_winner(self, battlemaster_classic):
        battlemaster_classic.player_placer.autoSetBoards(
            battlemaster_classic.player_field
        )
        battlemaster_classic.start()
        assert battlemaster_classic.check_winner() is None

    def test_check_winner_player_wins(self, battlemaster_classic):
        battlemaster_classic.start()
        for ship in battlemaster_classic.bot_field.boards:
            ship.hits = ship.size()
        assert battlemaster_classic.check_winner() == "player"

    def test_check_winner_bot_wins(self, battlemaster_classic):
        battlemaster_classic.player_placer.autoSetBoards(
            battlemaster_classic.player_field
        )
        battlemaster_classic.start()
        for ship in battlemaster_classic.player_field.boards:
            ship.hits = ship.size()
        assert battlemaster_classic.check_winner() == "bot"

    def test_watch_methods(self, battlemaster_classic):
        assert "Поле игрока" in battlemaster_classic.watch_my_field()
        assert "Поле бота" in battlemaster_classic.watch_opp_field()

    def test_bot_different_types(self):
        bm_smart = BattleMaster(bot_type="smart")
        bm_random = BattleMaster(bot_type="random")
        assert bm_smart.bot.bot_type == "smart"
        assert bm_random.bot.bot_type == "random"
