"""Unit tests for recallstorm.scenario_gs1.lot_pull."""
from datetime import datetime
from contract import Facing, Location, Store, StoreFormat
from recallstorm.core.jsonl import validate_record
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


def test_scenario_gs1_lot_pull():
    st = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    f1 = Facing("WM1", "S1", Location("A01", 1, 1, 1), 10)
    f2 = Facing("WM1", "S2", Location("A01", 2, 1, 1), 8)
    as_of = datetime.fromisoformat("2026-12-30T18:00:00-08:00")
    dl = datetime.fromisoformat("2027-01-01T00:00:00-08:00")
    win = lot_task_window(as_of, dl)

    shelf_lots = {"S1": ["L2601"]}
    assert lots_on_shelf("S1", shelf_lots) == ["L2601"]
    ev = lot_evidence("S1", "L2601", "REC1")
    assert validate_record(ev, "evidence") == []
    vt = lot_verify_task("WM1", f2, "A1", win, 1)
    assert validate_record(vt, "shelf_task") == []

    tasks = lot_pull_tasks(st, [f1, f2], ["L26*"], shelf_lots, "A1", win)
    assert len(tasks) == 2
    counts = lot_pull_counts(tasks)
    assert counts["PULL"] == 1 and counts["HOLD_VERIFY"] == 1
    assert lot_quarantine("WM1", "S1", "L2601", 10)["status"] == "QUARANTINED"
    assert lot_report(tasks)["total_tasks"] == 2
    assert LotPuller(["L26*"]).target_lots == ["L26*"]
