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


def test_sim_events(tmp_path):
    loc = {"aisle": "A01", "bay": 1, "shelf": 1, "pos": 1}
    e1 = MoveEvent("2026-12-30T22:00:00-08:00", "WM1", "A1", loc, "T1")
    e2 = PullEvent("2026-12-30T22:01:00-08:00", "WM1", "A1", loc, "T1")
    e3 = PlaceEvent("2026-12-30T22:02:00-08:00", "WM1", "A1", loc, "T1")
    e4 = DoneEvent("2026-12-30T22:03:00-08:00", "WM1", "A1", loc, "T1")

    recs = [event_to_record(e) for e in (e4, e2, e1, e3)]
    ordered = sort_events(recs)
    assert [r["kind"] for r in ordered] == ["MOVE", "PULL", "PLACE", "DONE"]
    assert len(events_for_store(ordered, "WM1")) == 4
    assert len(events_for_associate(ordered, "A1")) == 4
    out = tmp_path / "events.jsonl"
    assert events_to_jsonl(ordered, str(out)) == 4
