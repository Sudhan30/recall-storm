"""Unit tests for recallstorm.labor.assign."""
from datetime import datetime
from contract import Associate
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


def test_labor_assign():
    t0 = datetime.fromisoformat("2026-12-30T22:00:00-08:00")
    t1 = datetime.fromisoformat("2026-12-31T06:00:00-08:00")
    deadline = datetime.fromisoformat("2027-01-01T00:00:00-08:00")
    a1 = Associate("WM1-A01", "WM1", "D01", False, t0, t1)
    flt = Associate("FLT-D01", None, "D01", True, t0, t1)
    tasks = [
        {"task_id": "T1", "store_id": "WM1", "action": "PULL", "qty_units": 10},
        {"task_id": "T2", "store_id": "WM1", "action": "TAG_FLASH", "qty_units": 1},
    ]
    assigned = assign_tasks(tasks, [a1], deadline=deadline)
    assert len(assigned) == 2
    assert assignment_conflicts(assigned) == []
    assert "WM1-A01" in balance_load(tasks, [a1], deadline)
    assert len(greedy_assign(tasks, [a1], deadline)) == 2
    assert len(assign_floaters(tasks, [flt], deadline)) == 2
    assert len(reassign_overflow(tasks, [a1], [flt], deadline)) == 2
    assert assignment_summary(assigned)["total_tasks"] == 2
    assert len(assignment_to_records(assigned)) == 2
    assert len(LaborPlan(assigned).tasks) == 2
