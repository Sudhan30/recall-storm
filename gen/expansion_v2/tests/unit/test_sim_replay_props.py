"""Property tests for recallstorm.sim.replay."""
from recallstorm.sim.replay import replay_tasks


def test_every_task_emits_three_ordered_events():
    tasks = [
        {
            "type": "shelf_task",
            "task_id": f"TSK-{i}",
            "store_id": "WM1",
            "sku_id": "S1",
            "action": "PULL" if i % 2 == 0 else "TAG_FLASH",
            "loc": {"aisle": "A01", "bay": i + 1, "shelf": 1, "pos": 1},
            "qty_units": 5,
            "associate_id": "A1",
            "window": ["2026-12-30T22:00:00-08:00", "2026-12-30T22:05:00-08:00"],
        }
        for i in range(15)
    ]
    evs = replay_tasks(tasks)
    assert len(evs) == 45
    assert sum(1 for e in evs if e["kind"] == "DONE") == 15
