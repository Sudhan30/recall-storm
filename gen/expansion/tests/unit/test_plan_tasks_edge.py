"""Edge tests for recallstorm.plan.tasks."""
from datetime import datetime
from contract import Facing, Location, Store, StoreFormat
from recallstorm.plan.tasks import (
    build_shelf_tasks,
    task_window,
)


def test_tasks_edge():
    dl = datetime.fromisoformat("2027-01-01T00:00:00-08:00")
    late_start = datetime.fromisoformat("2027-01-01T02:00:00-08:00")
    win = task_window(late_start, 10, dl)
    assert datetime.fromisoformat(win[1]) < dl

    st = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    f = Facing("WM1", "S1", Location("A01", 1, 1, 1), 10)
    assert build_shelf_tasks(st, [f], {}, {}, {}, {}, [], dl) == []
