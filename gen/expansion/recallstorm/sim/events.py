"""Discrete simulation events (MOVE, PULL, PLACE, DONE) for events.jsonl."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from recallstorm.core.jsonl import write_jsonl

VALID_EVENT_KINDS = ("MOVE", "PULL", "PLACE", "DONE")


@dataclass(frozen=True)
class MoveEvent:
    """Associate movement to a shelf location."""

    t: str
    store_id: str
    associate_id: str
    loc: dict
    task_id: str
    kind: str = "MOVE"


@dataclass(frozen=True)
class PullEvent:
    """Associate pulling recalled/held product from a shelf."""

    t: str
    store_id: str
    associate_id: str
    loc: dict
    task_id: str
    kind: str = "PULL"


@dataclass(frozen=True)
class PlaceEvent:
    """Associate placing a substitute or flash tag at a shelf location."""

    t: str
    store_id: str
    associate_id: str
    loc: dict
    task_id: str
    kind: str = "PLACE"


@dataclass(frozen=True)
class DoneEvent:
    """Completion of a shelf task."""

    t: str
    store_id: str
    associate_id: str
    loc: dict
    task_id: str
    kind: str = "DONE"


def event_to_record(ev: MoveEvent | PullEvent | PlaceEvent | DoneEvent | dict) -> dict:
    """Convert an event dataclass or dict into the canonical events.jsonl schema."""
    if isinstance(ev, dict):
        kind = str(ev.get("kind", "MOVE"))
        if kind not in VALID_EVENT_KINDS:
            raise ValueError(f"Invalid event kind: {kind}")
        return {
            "t": str(ev["t"]),
            "store_id": str(ev["store_id"]),
            "associate_id": str(ev["associate_id"]),
            "kind": kind,
            "loc": dict(ev["loc"]),
            "task_id": str(ev["task_id"]),
        }
    if isinstance(ev, (MoveEvent, PullEvent, PlaceEvent, DoneEvent)):
        return {
            "t": ev.t,
            "store_id": ev.store_id,
            "associate_id": ev.associate_id,
            "kind": ev.kind,
            "loc": dict(ev.loc),
            "task_id": ev.task_id,
        }
    raise TypeError(f"Unsupported event object: {type(ev)}")


def sort_events(events: list[dict]) -> list[dict]:
    """Deterministically sort event records chronologically by (t, store_id, associate_id, task_id)."""
    order_rank = {"MOVE": 1, "PULL": 2, "PLACE": 3, "DONE": 4}
    return sorted(
        events,
        key=lambda e: (
            str(e.get("t", "")),
            str(e.get("store_id", "")),
            str(e.get("associate_id", "")),
            str(e.get("task_id", "")),
            order_rank.get(str(e.get("kind", "")), 9),
        ),
    )


def events_for_store(events: list[dict], store_id: str) -> list[dict]:
    """Filter events belonging to store_id."""
    return [e for e in events if e.get("store_id") == store_id]


def events_for_associate(events: list[dict], associate_id: str) -> list[dict]:
    """Filter events belonging to associate_id."""
    return [e for e in events if e.get("associate_id") == associate_id]


def events_to_jsonl(events: list[dict], path: str | Path) -> int:
    """Write sorted event records to events.jsonl and return count written."""
    normalized = [event_to_record(e) for e in events]
    return write_jsonl(path, sort_events(normalized))
