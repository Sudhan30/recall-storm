"""Unit tests for recallstorm.sim.metrics."""
from contract import Store, StoreFormat
from recallstorm.sim.metrics import (
    MetricsReport,
    completion_curve,
    district_completion,
    idle_minutes,
    late_tasks,
    placed_units_by,
    pulled_units_by,
    store_completion,
    tasks_done_by,
)
from recallstorm.sim.replay import replay_tasks


def test_simulation_metrics():
    loc = {"aisle": "A01", "bay": 1, "shelf": 1, "pos": 1}
    tasks = [
        {
            "task_id": "TSK-1",
            "store_id": "WM1",
            "associate_id": "A1",
            "action": "PULL",
            "qty_units": 10,
            "loc": loc,
            "window": ["2026-12-30T22:00:00-08:00", "2026-12-30T22:05:00-08:00"],
        },
        {
            "task_id": "TSK-2",
            "store_id": "WM1",
            "associate_id": "A1",
            "action": "PLACE_SUB",
            "qty_units": 8,
            "loc": loc,
            "window": ["2026-12-30T22:15:00-08:00", "2026-12-30T22:20:00-08:00"],
        },
    ]
    evs = replay_tasks(tasks)
    tmap = {t["task_id"]: t for t in tasks}
    dl = "2027-01-01T00:00:00-08:00"

    curve = completion_curve(evs)
    assert len(curve) == 2 and curve[-1][1] == 2
    assert tasks_done_by(evs, dl) == 2
    assert pulled_units_by(evs, tmap, dl) == 10
    assert placed_units_by(evs, tmap, dl) == 8
    assert store_completion(evs, "WM1") == 1.0
    st = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    assert district_completion(evs, {"WM1": st}, "D01") == 1.0
    assert late_tasks(evs, dl) == []
    assert idle_minutes(evs, "A1") > 0.0
    rep = MetricsReport(2, 0, 1.0)
    assert rep.completion_rate == 1.0
