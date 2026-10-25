"""Unit tests for recallstorm.store.backroom."""
from contract import Facing, Location
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


def test_store_backroom():
    loc = staging_area("WM1563")
    assert loc.aisle == "BACKROOM"
    assert len(backroom_locations("WM1563")) == 4
    assert backroom_stock("WM1563", "S1", 12)["units"] == 12
    f = Facing("WM1563", "S1", Location("A01", 2, 3, 4), 10)
    ts = topstock_for_sku([f], "S1")
    assert ts[0].shelf == 99
    tsk = backroom_pull_task("WM1563", "S1", 12)
    assert tsk["action"] == "PULL"
    assert backroom_capacity_left(100, 500) == 400
    assert stage_returns("WM1563", 10)["staged_cases"] == 10
    assert backroom_summary("WM1563", 10)["capacity_left"] == 490
    br = Backroom("WM1563", 500, 10)
    assert br.staged_cases == 10
