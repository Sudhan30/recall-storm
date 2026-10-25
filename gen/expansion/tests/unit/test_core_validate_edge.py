"""Edge tests for recallstorm.core.validate."""
from datetime import datetime, timezone
from contract import Associate, Facing, Location, Rule, Sku, Store, StoreFormat, Truck
from recallstorm.core.validate import (
    validate_associate,
    validate_datapack,
    validate_facing,
    validate_rule,
    validate_sku,
    validate_store,
    validate_truck,
)


def test_invalid_entities():
    bad_sku = Sku("", "ABC", "N", "B", "C", "I", True, False, 0, -1.0, 0.0)
    assert len(validate_sku(bad_sku)) >= 4

    bad_store = Store("", StoreFormat.DISCOUNT, "CA", "City", 100.0, -200.0, "D1", "", "")
    assert len(validate_store(bad_store)) >= 3

    bad_facing = Facing("", "", Location("", 0, 0, 0), 0)
    assert len(validate_facing(bad_facing)) >= 3

    dt = datetime(2026, 12, 30, 22, 0, tzinfo=timezone.utc)
    bad_assoc = Associate("", None, "D1", False, dt, dt)
    assert len(validate_associate(bad_assoc)) >= 2

    bad_truck = Truck("", "", 0.0, -5.0, dt)
    assert len(validate_truck(bad_truck)) >= 3

    bad_rule = Rule("", "", (), (), (), dt, "", "")
    assert len(validate_rule(bad_rule)) >= 5

    assert validate_datapack("not_a_pack") != []  # type: ignore[arg-type]
