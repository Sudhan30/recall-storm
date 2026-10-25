"""Property tests for recallstorm.sim.events."""
from recallstorm.sim.events import DoneEvent, MoveEvent, PlaceEvent, PullEvent, event_to_record


def test_all_event_classes_produce_valid_kinds():
    loc = {"aisle": "A01", "bay": 1, "shelf": 1, "pos": 1}
    for cls in (MoveEvent, PullEvent, PlaceEvent, DoneEvent):
        rec = event_to_record(cls("2026-12-30T22:00:00-08:00", "WM1", "A1", loc, "T1"))
        assert rec["kind"] in {"MOVE", "PULL", "PLACE", "DONE"}
        assert set(rec.keys()) == {"t", "store_id", "associate_id", "kind", "loc", "task_id"}
