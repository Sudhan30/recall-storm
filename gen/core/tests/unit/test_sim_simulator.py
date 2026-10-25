"""Unit tests for recallstorm.sim."""
from __future__ import annotations

from datetime import datetime
from recallstorm.sim import simulate_events


def test_simulate_events_generates_move_action_done_in_order() -> None:
    plan_records = [
        {
            "type": "shelf_task",
            "task_id": "TASK-00001",
            "store_id": "CA1000",
            "sku_id": "SKU00000",
            "action": "PULL",
            "loc": {"aisle": "A01", "bay": 1, "shelf": 1, "pos": 1},
            "qty_units": 12,
            "associate_id": "CA1000-A00",
            "window": ["2026-12-30T22:00:00-08:00", "2026-12-30T22:04:00-08:00"],
            "seq": 1,
            "evidence_id": "EV-00000",
            "sub_sku_id": None,
            "alloc_id": None,
            "src": "recallstorm/plan/planner.py",
        },
        {
            "type": "shelf_task",
            "task_id": "TASK-00002",
            "store_id": "CA1000",
            "sku_id": "SKU00000",
            "action": "PLACE_SUB",
            "loc": {"aisle": "A01", "bay": 1, "shelf": 1, "pos": 1},
            "qty_units": 12,
            "associate_id": "CA1000-A00",
            "window": ["2026-12-30T22:04:00-08:00", "2026-12-30T22:08:00-08:00"],
            "seq": 2,
            "evidence_id": "EV-00000",
            "sub_sku_id": "SKU00112",
            "alloc_id": "ALLOC-00000",
            "src": "recallstorm/plan/planner.py",
        },
    ]

    events = simulate_events(plan_records)
    assert len(events) == 6
    kinds = [e["kind"] for e in events]
    assert kinds == ["MOVE", "PULL", "DONE", "MOVE", "PLACE", "DONE"]

    times = [datetime.fromisoformat(e["t"]) for e in events]
    assert times == sorted(times)
    for e in events:
        assert set(e.keys()) == {"t", "store_id", "associate_id", "kind", "loc", "task_id"}
