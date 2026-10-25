"""Property tests for recallstorm.labor.assign."""
from datetime import datetime
from contract import Associate
from recallstorm.labor.assign import assign_tasks


def test_assigned_windows_strictly_before_deadline():
    t0 = datetime.fromisoformat("2026-12-30T22:00:00-08:00")
    t1 = datetime.fromisoformat("2026-12-31T06:00:00-08:00")
    deadline = datetime.fromisoformat("2026-12-31T04:00:00-08:00")
    a = Associate("WM1-A01", "WM1", "D01", False, t0, t1)
    tasks = [{"task_id": f"T{i}", "store_id": "WM1", "action": "PULL", "qty_units": 20} for i in range(25)]
    assigned = assign_tasks(tasks, [a], deadline=deadline)
    for t in assigned:
        end_dt = datetime.fromisoformat(t["window"][1])
        assert end_dt < deadline
