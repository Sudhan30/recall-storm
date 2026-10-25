"""Compute completion curves, pulled units, and lateness metrics from events."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from contract import Store
from recallstorm.core.clock import is_before_deadline, minutes_between


@dataclass
class MetricsReport:
    """Simulation KPI report."""

    total_done: int
    late_count: int


def completion_curve(events: list[dict]) -> list[tuple[str, int]]:
    """Return cumulative (timestamp_iso, tasks_completed) points for DONE events."""
    done_evs = sorted([e for e in events if e.get("kind") == "DONE"], key=lambda x: str(x.get("t", "")))
    out: list[tuple[str, int]] = []
    for idx, e in enumerate(done_evs, 1):
        out.append((str(e["t"]), idx))
    return out


def tasks_done_by(events: list[dict], cutoff_iso: str) -> int:
    """Count DONE events with timestamp <= cutoff_iso."""
    cutoff = datetime.fromisoformat(cutoff_iso)
    return sum(
        1
        for e in events
        if e.get("kind") == "DONE" and is_before_deadline(datetime.fromisoformat(e["t"]), cutoff, strict=False)
    )


def pulled_units_by(events: list[dict], tasks: list[dict], cutoff_iso: str) -> int:
    """Sum qty_units of PULL tasks completed by cutoff_iso."""
    cutoff = datetime.fromisoformat(cutoff_iso)
    done_ids = {
        e["task_id"]
        for e in events
        if e.get("kind") == "DONE" and is_before_deadline(datetime.fromisoformat(e["t"]), cutoff, strict=False)
    }
    return sum(int(t.get("qty_units", 0)) for t in tasks if t.get("task_id") in done_ids and t.get("action") == "PULL")


def placed_units_by(events: list[dict], tasks: list[dict], cutoff_iso: str) -> int:
    """Sum qty_units of PLACE_SUB tasks completed by cutoff_iso."""
    cutoff = datetime.fromisoformat(cutoff_iso)
    done_ids = {
        e["task_id"]
        for e in events
        if e.get("kind") == "DONE" and is_before_deadline(datetime.fromisoformat(e["t"]), cutoff, strict=False)
    }
    return sum(
        int(t.get("qty_units", 0)) for t in tasks if t.get("task_id") in done_ids and t.get("action") == "PLACE_SUB"
    )


def store_completion(events: list[dict], store_id: str) -> dict:
    """Compute DONE task count and last timestamp for store_id."""
    st_done = [e for e in events if e.get("store_id") == store_id and e.get("kind") == "DONE"]
    last_t = max((str(e["t"]) for e in st_done), default=None)
    return {"store_id": store_id, "done_tasks": len(st_done), "last_done": last_t}


def district_completion(events: list[dict], stores: list[Store]) -> dict[str, int]:
    """Sum completed tasks per store district."""
    st_to_dist = {s.store_id: s.district for s in stores}
    out = {s.district: 0 for s in stores}
    for e in events:
        if e.get("kind") == "DONE":
            d = st_to_dist.get(str(e.get("store_id", "")))
            if d:
                out[d] = out.get(d, 0) + 1
    return out


def late_tasks(events: list[dict], deadline_iso: str) -> list[str]:
    """Return task_ids of DONE events occurring at or after deadline_iso."""
    dl = datetime.fromisoformat(deadline_iso)
    return [
        str(e["task_id"])
        for e in events
        if e.get("kind") == "DONE" and not is_before_deadline(datetime.fromisoformat(e["t"]), dl, strict=True)
    ]


def idle_minutes(events: list[dict], associate_id: str) -> float:
    """Compute elapsed minutes between consecutive tasks for associate_id."""
    a_evs = sorted(
        [e for e in events if e.get("associate_id") == associate_id],
        key=lambda x: str(x.get("t", "")),
    )
    if len(a_evs) < 2:
        return 0.0
    idle = 0.0
    for i in range(1, len(a_evs)):
        if a_evs[i - 1].get("kind") == "DONE" and a_evs[i].get("kind") == "MOVE":
            gap = minutes_between(datetime.fromisoformat(a_evs[i - 1]["t"]), datetime.fromisoformat(a_evs[i]["t"]))
            if gap > 0:
                idle += gap
    return round(idle, 2)
