"""Replay shelf tasks into chronological MOVE, PULL, PLACE, and DONE events."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from contract import Action, Location
from recallstorm.sim.events import (
    DoneEvent,
    MoveEvent,
    PlaceEvent,
    PullEvent,
    event_to_record,
    sort_events,
)
from recallstorm.store.layout import walking_distance


@dataclass(frozen=True)
class Replayer:
    """Discrete-event replayer for shelf_task records."""

    speed_fps: float = 4.0


def walking_time(loc1: Location | dict, loc2: Location | dict) -> float:
    """Return walking time in seconds between two shelf locations."""
    l1 = Location(**loc1) if isinstance(loc1, dict) else loc1
    l2 = Location(**loc2) if isinstance(loc2, dict) else loc2
    return round(walking_distance(l1, l2) / 4.0, 2)


def event_times(window_start: str, window_end: str, steps: int = 3) -> list[str]:
    """Generate `steps` monotonically increasing ISO timestamps within [window_start, window_end]."""
    if steps <= 0:
        return []
    s = datetime.fromisoformat(window_start)
    e = datetime.fromisoformat(window_end)
    total_secs = max(steps, int((e - s).total_seconds()))
    stride = max(1, total_secs // (steps + 1))
    return [(s + timedelta(seconds=stride * i)).isoformat(timespec="seconds") for i in range(steps)]


def replay_tasks(tasks: list[dict]) -> list[dict]:
    """Replay a list of shelf_task records into sorted MOVE, PULL/PLACE, and DONE events."""
    events: list[dict] = []
    for t in tasks:
        w = t.get("window", ["2026-12-30T22:00:00-08:00", "2026-12-30T22:05:00-08:00"])
        ts = event_times(w[0], w[1], 3)
        st_id = str(t["store_id"])
        assoc_id = str(t["associate_id"])
        loc = dict(t["loc"])
        tid = str(t["task_id"])
        act = str(t.get("action", Action.PULL.value))

        events.append(event_to_record(MoveEvent(ts[0], st_id, assoc_id, loc, tid)))
        if act in (Action.PULL.value, Action.HOLD_VERIFY.value):
            events.append(event_to_record(PullEvent(ts[1], st_id, assoc_id, loc, tid)))
        else:
            events.append(event_to_record(PlaceEvent(ts[1], st_id, assoc_id, loc, tid)))
        events.append(event_to_record(DoneEvent(ts[2], st_id, assoc_id, loc, tid)))

    return sort_events(events)


def replay_store(tasks: list[dict], store_id: str) -> list[dict]:
    """Replay only the shelf tasks belonging to store_id."""
    return replay_tasks([t for t in tasks if t.get("store_id") == store_id])


def replay_associate(tasks: list[dict], associate_id: str) -> list[dict]:
    """Replay only the shelf tasks assigned to associate_id."""
    return replay_tasks([t for t in tasks if t.get("associate_id") == associate_id])


def simulate_plan(plan_records: list[dict]) -> list[dict]:
    """Extract all shelf_task records from plan_records and simulate their event stream."""
    tasks = [r for r in plan_records if r.get("type") == "shelf_task"]
    return replay_tasks(tasks)


def detect_late_events(events: list[dict], deadline_iso: str) -> list[dict]:
    """Return any events whose timestamp t is >= deadline_iso."""
    dl = datetime.fromisoformat(deadline_iso)
    return [e for e in events if datetime.fromisoformat(e["t"]) >= dl]


def replay_summary(events: list[dict]) -> dict:
    """Summarize event counts by kind across an event stream."""
    by_kind: dict[str, int] = {"MOVE": 0, "PULL": 0, "PLACE": 0, "DONE": 0}
    for e in events:
        k = str(e.get("kind", ""))
        if k in by_kind:
            by_kind[k] += 1
    return {"total_events": len(events), "by_kind": by_kind}
