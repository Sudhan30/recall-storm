"""Unit tests for recallstorm.core.validate."""
from datetime import datetime
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
    StoreNote,
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


def test_validate_valid_entities():
    sku = Sku("S1", "00012345678905", "Candy", "Brand", "candy", "SUGAR", True, False, 12, 1.5, 5.0)
    store = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    facing = Facing("WM1", "S1", Location("A01", 1, 1, 1), 10)
    t0 = datetime.fromisoformat("2026-12-30T22:00:00-08:00")
    t1 = datetime.fromisoformat("2026-12-31T06:00:00-08:00")
    assoc = Associate("A1", "WM1", "D01", False, t0, t1)
    truck = Truck("T1", "DC1", 3400.0, 40000.0, t1)
    rule = Rule("R1", "RED3", ("Red 3",), ("CA",), ("food",), datetime(2027, 1, 1), "ref", "txt")

    assert validate_sku(sku) == []
    assert validate_store(store) == []
    assert validate_facing(facing) == []
    assert validate_associate(assoc) == []
    assert validate_truck(truck) == []
    assert validate_rule(rule) == []

    pack = DataPack(
        skus=[sku],
        stores=[store],
        facings=[facing],
        associates=[assoc],
        trucks=[truck],
        dc_stock=[DcStock("DC1", "S1", 5)],
        substitutes={},
        notes=[StoreNote("N1", "WM1", "ok")],
        rules=[rule],
        as_of=t0,
    )
    assert validate_datapack(pack) == []
    summary = issues_summary(collect_issues(pack))
    assert summary["total"] == 0
