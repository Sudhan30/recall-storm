"""Replay shelf tasks into ordered discrete simulation events."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from contract import Location
from recallstorm.core.clock import is_before_deadline, iso_with_offset
from recallstorm.sim.events import DoneEvent, MoveEvent, PlaceEvent, PullEvent, event_to_record, sort_events
from recallstorm.sim.walking import walk_seconds


@dataclass
class Replayer:
    """Discrete-event simulator replaying shelf tasks into events.jsonl records."""

    deadline: datetime | None = None

    def run(self, plan_records: list[dict]) -> list[dict]:
        return simulate_plan(plan_records, deadline=self.deadline)


def walking_time(loc1: dict, loc2: dict) -> float:
    """Compute walking time in seconds between two location dictionaries."""
    l1 = Location(str(loc1.get("aisle", "A01")), int(loc1.get("bay", 1)), int(loc1.get("shelf", 1)), int(loc1.get("pos", 1)))
    l2 = Location(str(loc2.get("aisle", "A01")), int(loc2.get("bay", 1)), int(loc2.get("shelf", 1)), int(loc2.get("pos", 1)))
    return walk_seconds(l1, l2)


def event_times(task: dict) -> tuple[str, str, str]:
    """Compute (move_iso, action_iso, done_iso) within task['window']."""
    win = task.get("window") or ["2026-12-30T22:00:00-08:00", "2026-12-30T22:10:00-08:00"]
    s = datetime.fromisoformat(win[0])
    e = datetime.fromisoformat(win[1])
    if e <= s:
        e = s + timedelta(seconds=60)
    span_sec = max(3.0, (e - s).total_seconds())
    t_move = s
    t_act = s + timedelta(seconds=span_sec * 0.3)
    t_done = e
    return (iso_with_offset(t_move), iso_with_offset(t_act), iso_with_offset(t_done))


def replay_tasks(tasks: list[dict], deadline: datetime | None = None) -> list[dict]:
    """Replay a list of shelf_task records into MOVE, PULL/PLACE, and DONE events."""
    events: list[dict] = []
    for t in tasks:
        if t.get("type", "shelf_task") != "shelf_task":
            continue
        t_move, t_act, t_done = event_times(t)
        if deadline is not None:
            dt_done = datetime.fromisoformat(t_done)
            if dt_done >= deadline:
                safe_done = deadline - timedelta(seconds=30)
                t_done = iso_with_offset(safe_done)
                t_act = iso_with_offset(safe_done - timedelta(seconds=20))
                t_move = iso_with_offset(safe_done - timedelta(seconds=40))

        st_id = str(t["store_id"])
        assoc_id = str(t["associate_id"])
        tid = str(t["task_id"])
        loc = dict(t["loc"])
        act = str(t.get("action", "PULL")).upper()

        events.append(event_to_record(MoveEvent(t_move, st_id, assoc_id, loc, tid)))
        if act in {"PULL", "HOLD_VERIFY"}:
            events.append(event_to_record(PullEvent(t_act, st_id, assoc_id, loc, tid)))
        else:
            events.append(event_to_record(PlaceEvent(t_act, st_id, assoc_id, loc, tid)))
        events.append(event_to_record(DoneEvent(t_done, st_id, assoc_id, loc, tid)))

    return sort_events(events)


def replay_store(store_id: str, tasks: list[dict], deadline: datetime | None = None) -> list[dict]:
    """Replay tasks for a single store_id."""
    st_tasks = [t for t in tasks if t.get("store_id") == store_id]
    return replay_tasks(st_tasks, deadline=deadline)


def replay_associate(associate_id: str, tasks: list[dict], deadline: datetime | None = None) -> list[dict]:
    """Replay tasks assigned to a single associate_id."""
    a_tasks = [t for t in tasks if t.get("associate_id") == associate_id]
    return replay_tasks(a_tasks, deadline=deadline)


def simulate_plan(plan_records: list[dict], deadline: datetime | None = None) -> list[dict]:
    """Extract shelf_task records from plan_records and simulate all discrete events."""
    tasks = [r for r in plan_records if r.get("type") == "shelf_task"]
    return replay_tasks(tasks, deadline=deadline)


def detect_late_events(events: list[dict], deadline: datetime) -> list[dict]:
    """Return any events whose timestamp 't' is at or after deadline."""
    return [
        e for e in events if not is_before_deadline(datetime.fromisoformat(e["t"]), deadline, strict=True)
    ]


def replay_summary(events: list[dict]) -> dict:
    """Summarize replayed simulation events by kind."""
    by_kind = {"MOVE": 0, "PULL": 0, "PLACE": 0, "DONE": 0}
    for e in events:
        k = str(e.get("kind", ""))
        by_kind[k] = by_kind.get(k, 0) + 1
    return {"total_events": len(events), "by_kind": by_kind}
