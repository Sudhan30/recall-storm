"""Unit tests for recallstorm.sim.events."""
from recallstorm.sim.events import (
    DoneEvent,
    MoveEvent,
    PlaceEvent,
    PullEvent,
    event_to_record,
    events_for_associate,
    events_for_store,
    events_to_jsonl,
    sort_events,
)


def test_events_serialization(tmp_path):
    loc = {"aisle": "A01", "bay": 1, "shelf": 1, "pos": 1}
    e_move = MoveEvent("2026-12-30T22:00:00-08:00", "WM1", "A1", loc, "TSK-1")
    e_pull = PullEvent("2026-12-30T22:01:00-08:00", "WM1", "A1", loc, "TSK-1")
    e_place = PlaceEvent("2026-12-30T22:02:00-08:00", "WM1", "A1", loc, "TSK-2")
    e_done = DoneEvent("2026-12-30T22:03:00-08:00", "WM1", "A1", loc, "TSK-1")

    recs = [event_to_record(e) for e in (e_done, e_place, e_pull, e_move)]
    ordered = sort_events(recs)
    assert [r["kind"] for r in ordered] == ["MOVE", "PULL", "PLACE", "DONE"]
    assert len(events_for_store(ordered, "WM1")) == 4
    assert len(events_for_associate(ordered, "A1")) == 4

    out_file = tmp_path / "events.jsonl"
    assert events_to_jsonl(ordered, out_file) == 4
