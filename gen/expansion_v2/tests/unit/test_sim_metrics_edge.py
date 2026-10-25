"""Edge case tests for recallstorm.sim.metrics."""
from recallstorm.sim.metrics import completion_curve, idle_minutes, late_tasks


def test_sim_metrics_edge():
    assert completion_curve([]) == []
    assert idle_minutes([], "A1") == 0.0
    ev = [{"t": "2027-01-01T00:00:00-08:00", "store_id": "WM1", "associate_id": "A1", "kind": "DONE", "loc": {}, "task_id": "T1"}]
    assert late_tasks(ev, "2027-01-01T00:00:00-08:00") == ["T1"]
