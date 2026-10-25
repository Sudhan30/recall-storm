"""Unit tests for recallstorm.sim.replay."""
from datetime import datetime
from recallstorm.sim.replay import (
    Replayer,
    detect_late_events,
    event_times,
    replay_associate,
    replay_store,
    replay_summary,
    replay_tasks,
    simulate_plan,
    walking_time,
)


def test_sim_replay():
    t1 = {
        "type": "shelf_task",
        "task_id": "TSK-1",
        "store_id": "WM1",
        "sku_id": "S1",
        "action": "PULL",
        "loc": {"aisle": "A01", "bay": 1, "shelf": 1, "pos": 1},
        "qty_units": 10,
        "associate_id": "WM1-A01",
        "window": ["2026-12-30T22:00:00-08:00", "2026-12-30T22:10:00-08:00"],
    }
    t2 = {**t1, "task_id": "TSK-2", "action": "PLACE_SUB"}
    dl = datetime.fromisoformat("2027-01-01T00:00:00-08:00")

    assert walking_time(t1["loc"], {"aisle": "A02", "bay": 2, "shelf": 1, "pos": 1}) > 0.0
    m_t, a_t, d_t = event_times(t1)
    assert m_t < a_t < d_t

    evs = replay_tasks([t1, t2], deadline=dl)
    assert len(evs) == 6
    assert len(replay_store("WM1", [t1], dl)) == 3
    assert len(replay_associate("WM1-A01", [t1], dl)) == 3
    assert len(simulate_plan([t1, t2], dl)) == 6
    assert detect_late_events(evs, dl) == []
    assert replay_summary(evs)["by_kind"]["DONE"] == 2
    assert len(Replayer(dl).run([t1])) == 3
