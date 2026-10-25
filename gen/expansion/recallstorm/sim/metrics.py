"""Operational completion curves and KPIs computed from simulation event streams."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from contract import Store


@dataclass(frozen=True)
class MetricsReport:
    """Summary of simulation completion metrics."""

    total_done: int
    late_count: int
    completion_rate: float


def completion_curve(events: list[dict]) -> list[tuple[str, int]]:
    """Return cumulative (timestamp_iso, done_count) points over DONE events."""
    done_evs = sorted([e for e in events if e.get("kind") == "DONE"], key=lambda e: str(e.get("t", "")))
    out: list[tuple[str, int]] = []
    for idx, ev in enumerate(done_evs, 1):
        out.append((str(ev["t"]), idx))
    return out


def tasks_done_by(events: list[dict], cutoff_iso: str) -> int:
    """Count DONE events occurring strictly before cutoff_iso."""
    cutoff = datetime.fromisoformat(cutoff_iso)
    return sum(
        1 for e in events
        if e.get("kind") == "DONE" and datetime.fromisoformat(str(e["t"])) < cutoff
    )


def pulled_units_by(events: list[dict], tasks_by_id: dict[str, dict], cutoff_iso: str) -> int:
    """Sum qty_units of PULL tasks completed before cutoff_iso."""
    cutoff = datetime.fromisoformat(cutoff_iso)
    total = 0
    for e in events:
        if e.get("kind") == "PULL" and datetime.fromisoformat(str(e["t"])) < cutoff:
            t = tasks_by_id.get(str(e.get("task_id")))
            total += int(t.get("qty_units", 0)) if t else 0
    return total


def placed_units_by(events: list[dict], tasks_by_id: dict[str, dict], cutoff_iso: str) -> int:
    """Sum qty_units of PLACE_SUB tasks completed before cutoff_iso."""
    cutoff = datetime.fromisoformat(cutoff_iso)
    total = 0
    for e in events:
        if e.get("kind") == "PLACE" and datetime.fromisoformat(str(e["t"])) < cutoff:
            t = tasks_by_id.get(str(e.get("task_id")))
            if t and t.get("action") == "PLACE_SUB":
                total += int(t.get("qty_units", 0))
    return total


def store_completion(events: list[dict], store_id: str) -> float:
    """Compute fraction of initiated tasks in store_id that reached DONE."""
    st_evs = [e for e in events if e.get("store_id") == store_id]
    started = {e.get("task_id") for e in st_evs if e.get("kind") == "MOVE"}
    if not started:
        return 1.0
    done = {e.get("task_id") for e in st_evs if e.get("kind") == "DONE"}
    return round(len(started & done) / len(started), 4)


def district_completion(events: list[dict], stores_by_id: dict[str, Store], district: str) -> float:
    """Compute average store completion across all stores in a district."""
    dist_stores = [st_id for st_id, st in stores_by_id.items() if st.district == district]
    if not dist_stores:
        return 1.0
    rates = [store_completion(events, st_id) for st_id in dist_stores]
    return round(sum(rates) / len(rates), 4)


def late_tasks(events: list[dict], deadline_iso: str) -> list[str]:
    """Return sorted task_ids whose DONE event occurred at or after deadline_iso."""
    dl = datetime.fromisoformat(deadline_iso)
    return sorted(
        {
            str(e["task_id"]) for e in events
            if e.get("kind") == "DONE" and datetime.fromisoformat(str(e["t"])) >= dl
        }
    )


def idle_minutes(events: list[dict], associate_id: str) -> float:
    """Compute inter-task idle minutes (> 2 min gaps) for an associate."""
    a_evs = sorted(
        [e for e in events if e.get("associate_id") == associate_id],
        key=lambda e: str(e.get("t", "")),
    )
    if len(a_evs) < 2:
        return 0.0
    idle = 0.0
    for i in range(1, len(a_evs)):
        t1 = datetime.fromisoformat(str(a_evs[i - 1]["t"]))
        t2 = datetime.fromisoformat(str(a_evs[i]["t"]))
        gap = (t2 - t1).total_seconds() / 60.0
        if gap > 2.0:
            idle += gap - 2.0
    return round(idle, 2)
