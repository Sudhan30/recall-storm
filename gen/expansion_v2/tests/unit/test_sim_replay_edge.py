"""Edge case tests for recallstorm.sim.replay."""
from datetime import datetime
from recallstorm.sim.replay import detect_late_events, replay_tasks


def test_sim_replay_clamps_to_deadline():
    dl = datetime.fromisoformat("2027-01-01T00:00:00-08:00")
    late_task = {
        "type": "shelf_task",
        "task_id": "TSK-LATE",
        "store_id": "WM1",
        "sku_id": "S1",
        "action": "PULL",
        "loc": {"aisle": "A01", "bay": 1, "shelf": 1, "pos": 1},
        "qty_units": 5,
        "associate_id": "A1",
        "window": ["2026-12-31T23:55:00-08:00", "2027-01-01T00:10:00-08:00"],
    }
    evs = replay_tasks([late_task], deadline=dl)
    assert detect_late_events(evs, dl) == []
