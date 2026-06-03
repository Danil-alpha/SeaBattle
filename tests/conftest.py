import pytest
from field import Field
from ship_placer import ShipPlacer
from battle_master import BattleMaster


@pytest.fixture
def classic_field():
    return Field(field_type="classic", width=10, height=10)


@pytest.fixture
def hex_field():
    return Field(field_type="hex", radius=3)


@pytest.fixture
def classic_placer():
    return ShipPlacer(field_type="classic", width=10, height=10)


@pytest.fixture
def hex_placer():
    return ShipPlacer(field_type="hex", radius=3)


@pytest.fixture
def battlemaster_classic():
    return BattleMaster(field_type="classic", width=10, height=10, bot_type="smart")
