"""Unit tests for recallstorm.scenario_gs1.lot_pull."""
from contract import Facing, Location
from recallstorm.scenario_gs1.lot_pull import (
    LotPuller,
    lot_evidence,
    lot_pull_counts,
    lot_pull_tasks,
    lot_quarantine,
    lot_report,
    lot_task_window,
    lot_verify_task,
    lots_on_shelf,
)


def test_lot_pull_operations():
    lp = LotPuller(("L2601A",))
    assert lp.target_lots == ("L2601A",)
    f = Facing("SAMS4735", "FDC1034191", Location("A01", 1, 1, 1), 11)
    inv = {("SAMS4735", "FDC1034191"): ["L2601A"]}
    assert lots_on_shelf(f, inv) == ["L2601A"]

    win = lot_task_window("2026-12-30T18:00:00-08:00", "2027-01-01T00:00:00-08:00")
    ev = lot_evidence("FDC1034191", "L2601A")
    assert ev["type"] == "evidence"
    vt = lot_verify_task("SAMS4735", f, ["L2601A"], "A1", win, 1)
    assert vt["action"] == "HOLD_VERIFY"

    tasks = lot_pull_tasks("SAMS4735", [f], {"FDC1034191"}, ["L2601A"], "A1", win, inv)
    assert len(tasks) == 1 and tasks[0]["action"] == "PULL"
    q = lot_quarantine("SAMS4735", "FDC1034191", "L2601A", 11)
    assert q["units"] == 11
    assert lot_pull_counts(tasks)["total_units"] == 11
    assert lot_report(tasks)["stores"] == ["SAMS4735"]
