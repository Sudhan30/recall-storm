"""Unit tests for recallstorm.core.validate."""
from datetime import datetime, timezone
from contract import (
    Associate,
    DataPack,
    DcStock,
    Facing,
    Location,
    Rule,
    Sku,
    Store,
    StoreFormat,
    Truck,
)
from recallstorm.core.validate import (
    collect_issues,
    issues_summary,
    validate_associate,
    validate_datapack,
    validate_facing,
    validate_rule,
    validate_sku,
    validate_store,
    validate_truck,
)


def _sample_pack() -> DataPack:
    sku = Sku("S1", "00012345678905", "Candy", "Brand", "candy", "SUGAR", True, False, 12, 1.0, 5.0)
    store = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    facing = Facing("WM1", "S1", Location("A01", 1, 1, 1), 10)
    assoc = Associate(
        "A1",
        "WM1",
        "D01",
        False,
        datetime(2026, 12, 30, 22, 0, tzinfo=timezone.utc),
        datetime(2026, 12, 31, 6, 0, tzinfo=timezone.utc),
    )
    truck = Truck("T1", "DC1", 3400.0, 40000.0, datetime(2026, 12, 31, 8, 0, tzinfo=timezone.utc))
    rule = Rule("R1", "RED3", ("Red 3",), ("CA",), ("food",), datetime(2027, 1, 1), "ref", "src")
    return DataPack(
        [sku],
        [store],
        [facing],
        [assoc],
        [truck],
        [DcStock("DC1", "S1", 5)],
        {},
        [],
        [rule],
        datetime(2026, 12, 30, 18, 0, tzinfo=timezone.utc),
    )


def test_validate_valid_entities():
    pack = _sample_pack()
    assert validate_sku(pack.skus[0]) == []
    assert validate_store(pack.stores[0]) == []
    assert validate_facing(pack.facings[0]) == []
    assert validate_associate(pack.associates[0]) == []
    assert validate_truck(pack.trucks[0]) == []
    assert validate_rule(pack.rules[0]) == []
    assert validate_datapack(pack) == []
    summary = issues_summary(collect_issues(pack))
    assert summary["total"] == 0
