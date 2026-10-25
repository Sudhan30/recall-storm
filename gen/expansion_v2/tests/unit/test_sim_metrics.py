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


def test_sim_metrics():
    evs = [
        {"t": "2026-12-30T22:00:00-08:00", "store_id": "WM1", "associate_id": "A1", "kind": "MOVE", "loc": {}, "task_id": "T1"},
        {"t": "2026-12-30T22:05:00-08:00", "store_id": "WM1", "associate_id": "A1", "kind": "DONE", "loc": {}, "task_id": "T1"},
        {"t": "2026-12-30T22:15:00-08:00", "store_id": "WM1", "associate_id": "A1", "kind": "MOVE", "loc": {}, "task_id": "T2"},
        {"t": "2026-12-30T22:20:00-08:00", "store_id": "WM1", "associate_id": "A1", "kind": "DONE", "loc": {}, "task_id": "T2"},
    ]
    tasks = [
        {"task_id": "T1", "action": "PULL", "qty_units": 10},
        {"task_id": "T2", "action": "PLACE_SUB", "qty_units": 12},
    ]
    st = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")

    assert len(completion_curve(evs)) == 2
    assert tasks_done_by(evs, "2026-12-30T23:00:00-08:00") == 2
    assert pulled_units_by(evs, tasks, "2026-12-30T23:00:00-08:00") == 10
    assert placed_units_by(evs, tasks, "2026-12-30T23:00:00-08:00") == 12
    assert store_completion(evs, "WM1")["done_tasks"] == 2
    assert district_completion(evs, [st])["D01"] == 2
    assert late_tasks(evs, "2027-01-01T00:00:00-08:00") == []
    assert idle_minutes(evs, "A1") == 10.0
    assert MetricsReport(2, 0).total_done == 2
