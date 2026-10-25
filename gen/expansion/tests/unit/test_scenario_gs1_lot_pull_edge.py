"""Edge tests for recallstorm.scenario_gs1.lot_pull."""
import pytest
from contract import Facing, Location
from recallstorm.scenario_gs1.lot_pull import (
    lot_pull_tasks,
    lot_quarantine,
)


def test_lot_pull_edge():
    f = Facing("WM1", "S1", Location("A01", 1, 1, 1), 10)
    inv = {("WM1", "S1"): ["CLEAN_LOT"]}
    assert lot_pull_tasks("WM1", [f], {"S1"}, ["RECALLED_LOT"], "A1", ["2026-12-30", "2026-12-31"], inv) == []
    with pytest.raises(ValueError):
        lot_quarantine("WM1", "S1", "LOT1", 0)
