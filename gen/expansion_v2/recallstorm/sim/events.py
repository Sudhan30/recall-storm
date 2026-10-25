"""Discrete simulation events (MOVE, PULL, PLACE, DONE) for events.jsonl."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.jsonl import write_jsonl


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
    """Associate pulling recalled units from a shelf location."""

    t: str
    store_id: str
    associate_id: str
    loc: dict
    task_id: str
    kind: str = "PULL"


@dataclass(frozen=True)
class PlaceEvent:
    """Associate placing substitute units or flashing a tag at a shelf location."""

    t: str
    store_id: str
    associate_id: str
    loc: dict
    task_id: str
    kind: str = "PLACE"


@dataclass(frozen=True)
class DoneEvent:
    """Task completion event."""

    t: str
    store_id: str
    associate_id: str
    loc: dict
    task_id: str
    kind: str = "DONE"


def event_to_record(ev: MoveEvent | PullEvent | PlaceEvent | DoneEvent | dict) -> dict:
    """Serialize an event dataclass or dict to the exact events.jsonl schema:
    {"t": iso, "store_id", "associate_id", "kind": "MOVE"|"PULL"|"PLACE"|"DONE", "loc", "task_id"}.
    """
    if isinstance(ev, dict):
        kind = str(ev["kind"]).upper()
        if kind not in {"MOVE", "PULL", "PLACE", "DONE"}:
            raise ValueError(f"Invalid event kind: {kind!r}")
        return {
            "t": str(ev["t"]),
            "store_id": str(ev["store_id"]),
            "associate_id": str(ev["associate_id"]),
            "kind": kind,
            "loc": dict(ev["loc"]),
            "task_id": str(ev["task_id"]),
        }
    return {
        "t": ev.t,
        "store_id": ev.store_id,
        "associate_id": ev.associate_id,
        "kind": ev.kind,
        "loc": dict(ev.loc),
        "task_id": ev.task_id,
    }


def sort_events(events: list[dict]) -> list[dict]:
    """Sort event records chronologically by timestamp 't', then store_id, associate_id, task_id."""
    kind_order = {"MOVE": 0, "PULL": 1, "PLACE": 2, "DONE": 3}
    return sorted(
        events,
        key=lambda e: (
            str(e.get("t", "")),
            str(e.get("store_id", "")),
            str(e.get("associate_id", "")),
            str(e.get("task_id", "")),
            kind_order.get(str(e.get("kind", "")), 9),
        ),
    )


def events_for_store(events: list[dict], store_id: str) -> list[dict]:
    """Filter events by store_id."""
    return [e for e in events if e.get("store_id") == store_id]


def events_for_associate(events: list[dict], associate_id: str) -> list[dict]:
    """Filter events by associate_id."""
    return [e for e in events if e.get("associate_id") == associate_id]


def events_to_jsonl(events: list[dict], out_path: str) -> int:
    """Write sorted event records to out_path as JSONL."""
    ordered = sort_events([event_to_record(e) for e in events])
    return write_jsonl(out_path, ordered)
