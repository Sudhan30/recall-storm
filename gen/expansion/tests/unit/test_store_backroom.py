"""Unit tests for recallstorm.store.backroom."""
from contract import Facing, Location, Store, StoreFormat
from recallstorm.store.backroom import (
    Backroom,
    backroom_capacity_left,
    backroom_locations,
    backroom_pull_task,
    backroom_stock,
    backroom_summary,
    stage_returns,
    staging_area,
    topstock_for_sku,
)


def test_backroom_functions():
    st = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    f = Facing("WM1", "S1", Location("A01", 1, 1, 1), 20)
    assert staging_area("WM1").aisle == "BACKROOM"
    assert len(backroom_locations("WM1")) == 4
    assert backroom_stock([f], "WM1") == {"S1": 5}
    assert topstock_for_sku([f], "WM1", "S1") == 10
    task = backroom_pull_task("WM1", "S1", 5)
    assert task["action"] == "PULL"
    assert backroom_capacity_left(st, 50) == 250
    staged = stage_returns("WM1", {"S1": 3})
    assert staged["total_cases"] == 3
    br = Backroom("WM1", {"S1": 3})
    assert backroom_summary(br.store_id, br.staged_cases)["total_cases"] == 3
