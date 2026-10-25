"""Edge case tests for recallstorm.plan.tasks."""
from datetime import datetime
from contract import Store, StoreFormat
from recallstorm.plan.tasks import build_shelf_tasks, task_window


def test_plan_tasks_edge():
    st = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    dl = datetime.fromisoformat("2027-01-01T00:00:00-08:00")
    assert build_shelf_tasks(st, [], {}, {}, [], {}, [], dl) == []
    w = task_window(dl, 10.0, dl)
    assert datetime.fromisoformat(w[1]) < dl
