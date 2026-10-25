"""Unit tests for recallstorm.labor.assign."""
from datetime import datetime
from contract import Associate, Store, StoreFormat
from recallstorm.labor.assign import (
    LaborPlan,
    assign_floaters,
    assign_tasks,
    assignment_conflicts,
    assignment_summary,
    assignment_to_records,
    balance_load,
    greedy_assign,
    reassign_overflow,
)


def test_task_assignment():
    s = datetime.fromisoformat("2026-12-30T22:00:00-08:00")
    e = datetime.fromisoformat("2026-12-31T06:00:00-08:00")
    dl = datetime.fromisoformat("2027-01-01T00:00:00-08:00")
    st = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    a1 = Associate("WM1-A01", "WM1", "D01", False, s, e)
    flt = Associate("FLT-D01", None, "D01", True, s, e)

    raw_tasks = [
        {"task_id": "TSK-1", "action": "PULL", "qty_units": 12},
        {"task_id": "TSK-2", "action": "TAG_FLASH", "qty_units": 1},
    ]
    assigned = assign_tasks(raw_tasks, [a1, flt], st, dl)
    assert len(assigned) == 2
    assert assignment_conflicts(assigned, dl) == []
    assert assignment_summary(assigned)["total_tasks"] == 2
    assert len(assignment_to_records(assigned)) == 2
    assert len(greedy_assign(raw_tasks, [a1], dl)) == 2
    assert len(balance_load(raw_tasks, [a1], dl)) == 2
    assert len(assign_floaters(raw_tasks, [flt], st, dl)) == 2
    assert len(reassign_overflow(raw_tasks, [], [flt], dl)) == 2
    lp = LaborPlan("WM1", tuple(assigned), ("WM1-A01",))
    assert lp.store_id == "WM1"
