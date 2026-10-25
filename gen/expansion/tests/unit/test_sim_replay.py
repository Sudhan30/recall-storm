"""Unit tests for recallstorm.sim.replay."""
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


def test_replay_simulation():
    rep = Replayer()
    assert rep.speed_fps == 4.0
    l1 = {"aisle": "A01", "bay": 1, "shelf": 1, "pos": 1}
    l2 = {"aisle": "A01", "bay": 5, "shelf": 1, "pos": 1}
    assert walking_time(l1, l2) == 4.0

    ts = event_times("2026-12-30T22:00:00-08:00", "2026-12-30T22:10:00-08:00", 3)
    assert len(ts) == 3 and ts[0] < ts[1] < ts[2]

    tasks = [
        {
            "type": "shelf_task",
            "task_id": "TSK-1",
            "store_id": "WM1",
            "associate_id": "A1",
            "action": "PULL",
            "loc": l1,
            "window": ["2026-12-30T22:00:00-08:00", "2026-12-30T22:05:00-08:00"],
        },
        {
            "type": "shelf_task",
            "task_id": "TSK-2",
            "store_id": "WM1",
            "associate_id": "A1",
            "action": "PLACE_SUB",
            "loc": l2,
            "window": ["2026-12-30T22:06:00-08:00", "2026-12-30T22:12:00-08:00"],
        },
    ]
    evs = replay_tasks(tasks)
    assert len(evs) == 6
    assert len(replay_store(tasks, "WM1")) == 6
    assert len(replay_associate(tasks, "A1")) == 6
    assert len(simulate_plan(tasks)) == 6
    assert detect_late_events(evs, "2027-01-01T00:00:00-08:00") == []
    assert replay_summary(evs)["by_kind"]["DONE"] == 2
