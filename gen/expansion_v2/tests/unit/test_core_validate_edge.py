"""Edge case tests for recallstorm.core.validate."""
from datetime import datetime
from contract import Associate, Facing, Location, Rule, Sku, Store, StoreFormat, Truck
from recallstorm.core.validate import (
    validate_associate,
    validate_facing,
    validate_rule,
    validate_sku,
    validate_store,
    validate_truck,
)


def test_validate_invalid_entities():
    bad_sku = Sku("", "ABC", "", "", "", "", True, False, 0, -1.0, 0.0)
    assert len(validate_sku(bad_sku)) >= 4

    bad_store = Store("", StoreFormat.DISCOUNT, "CA", "X", 200.0, 0.0, "D1", "", "")
    assert len(validate_store(bad_store)) >= 3

    bad_facing = Facing("", "", Location("", -1, 1, 1), -5)
    assert len(validate_facing(bad_facing)) >= 3

    t = datetime.fromisoformat("2026-12-30T22:00:00-08:00")
    bad_assoc = Associate("", None, "D1", False, t, t)
    assert len(validate_associate(bad_assoc)) >= 3

    bad_truck = Truck("", "", 0.0, -10.0, t)
    assert len(validate_truck(bad_truck)) >= 3

    bad_rule = Rule("", "", (), (), (), t, "", "")
    assert len(validate_rule(bad_rule)) >= 5
