import pytest
from field import Field, CellState
from hit_maker import HitState
from bot import Bot


class TestRandomBotAI:
    def test_random_bot_make_move(self, classic_field):
        bot = Bot("random")
        bot.set_enemy_field(classic_field)
        for _ in range(20):
            target = bot.make_move()
            assert target is not None
            assert classic_field.is_valid_cell(*target)
        for q, r in classic_field.cells:
            classic_field.set_cell_state(q, r, CellState.HIT)
        assert bot.make_move() is None

    def test_random_bot_update_does_nothing(self, classic_field):
        bot = Bot("random")
        bot.set_enemy_field(classic_field)
        bot.update(0, 0, HitState.HIT)
        bot.update(1, 1, HitState.CRUSHED)


class TestSmartBotAI:
    def test_smart_bot_hunt_mode(self, classic_field):
        bot = Bot("smart")
        bot.set_enemy_field(classic_field)
        target = bot.make_move()
        assert target is not None
        assert classic_field.is_valid_cell(*target)

    def test_smart_bot_enters_target_mode_on_hit(self, classic_field):
        bot = Bot("smart")
        bot.set_enemy_field(classic_field)
        bot.update(1, 1, HitState.HIT)
        assert bot.ai.mode == "target"
        assert bot.ai.last_hit == (1, 1)
        neighbors = classic_field.get_neighbors(1, 1, include_diagonals=False)
        assert len(bot.ai.target_queue) == len(neighbors)
        assert set(bot.ai.target_queue) == set(neighbors)

    def test_smart_bot_target_queue_consumption(self, classic_field):
        bot = Bot("smart")
        bot.set_enemy_field(classic_field)
        bot.ai.mode = "target"
        bot.ai.target_queue = [(1, 1), (2, 2), (3, 3)]
        target = bot.make_move()
        assert target == (1, 1)
        target2 = bot.make_move()
        assert target2 == (2, 2)

    def test_smart_bot_returns_to_hunt_on_crushed(self, classic_field):
        bot = Bot("smart")
        bot.set_enemy_field(classic_field)
        bot.ai.mode = "target"
        bot.ai.target_queue = [(1, 1), (2, 2)]
        bot.update(3, 3, HitState.CRUSHED)
        assert bot.ai.mode == "hunt"
        assert bot.ai.target_queue == []
        assert bot.ai.last_hit is None

    def test_smart_bot_update_miss_does_nothing(self, classic_field):
        bot = Bot("smart")
        bot.set_enemy_field(classic_field)
        bot.ai.mode = "target"
        bot.ai.target_queue = [(1, 1)]
        bot.update(0, 0, HitState.MISS)
        assert bot.ai.mode == "target"
        assert len(bot.ai.target_queue) == 1

    def test_smart_bot_no_candidates(self, classic_field):
        bot = Bot("smart")
        bot.set_enemy_field(classic_field)
        for q, r in classic_field.cells:
            classic_field.set_cell_state(q, r, CellState.HIT)
        assert bot.make_move() is None
