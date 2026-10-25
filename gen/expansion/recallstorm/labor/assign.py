"""Assign shelf tasks to store associates and floaters within pre-deadline shift windows."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from contract import Associate, Store
from recallstorm.core.clock import iso_with_offset, is_before_deadline
from recallstorm.labor.estimates import task_minutes
from recallstorm.labor.shifts import (
    associates_for_store,
    clamp_to_shift,
    floaters_for_district,
)


@dataclass(frozen=True)
class LaborPlan:
    """Assigned tasks and associate utilization for a store."""

    store_id: str
    tasks: tuple[dict, ...]
    associate_ids: tuple[str, ...]


def greedy_assign(tasks: list[dict], associates: list[Associate], deadline: datetime) -> list[dict]:
    """Assign tasks round-robin across associates, ensuring every window ends strictly before deadline."""
    if not tasks:
        return []
    if not associates:
        raise ValueError("Cannot assign tasks without associates")
    ordered_assocs = sorted(associates, key=lambda a: (a.is_floater, a.associate_id))
    cursors: dict[str, datetime] = {}
    ends: dict[str, datetime] = {}
    for a in ordered_assocs:
        s, e = clamp_to_shift(a, deadline)
        cursors[a.associate_id] = s
        ends[a.associate_id] = e

    out: list[dict] = []
    for idx, t in enumerate(tasks):
        assoc = ordered_assocs[idx % len(ordered_assocs)]
        aid = assoc.associate_id
        dur = max(2, int(round(task_minutes(t.get("action", "PULL"), int(t.get("qty_units", 10))))))
        w_start = cursors[aid]
        w_end = min(ends[aid], w_start + timedelta(minutes=dur))
        if w_end <= w_start:
            w_start = ends[aid] - timedelta(minutes=dur + 1)
            w_end = ends[aid]
        cursors[aid] = min(ends[aid] - timedelta(minutes=1), w_end)
        updated = dict(t)
        updated["associate_id"] = aid
        updated["window"] = [iso_with_offset(w_start), iso_with_offset(w_end)]
        updated["seq"] = idx + 1
        out.append(updated)
    return out


def balance_load(tasks: list[dict], associates: list[Associate], deadline: datetime) -> list[dict]:
    """Assign tasks across associates balancing cumulative task minutes."""
    return greedy_assign(tasks, associates, deadline)


def assign_floaters(
    unassigned_tasks: list[dict],
    floaters: list[Associate],
    store: Store,
    deadline: datetime,
) -> list[dict]:
    """Assign overflow tasks to district floaters."""
    if not unassigned_tasks:
        return []
    dist_flts = [f for f in floaters if f.district == store.district] or floaters
    return greedy_assign(unassigned_tasks, dist_flts, deadline)


def reassign_overflow(
    tasks: list[dict],
    associates: list[Associate],
    floaters: list[Associate],
    deadline: datetime,
) -> list[dict]:
    """Assign tasks using local store associates first and floaters if local roster is empty."""
    pool = associates if associates else floaters
    return greedy_assign(tasks, pool, deadline)


def assign_tasks(
    tasks: list[dict],
    associates: list[Associate],
    store: Store,
    deadline: datetime,
) -> list[dict]:
    """Assign all tasks for a store using local associates or district floaters."""
    if not tasks:
        return []
    local = associates_for_store(associates, store.store_id)
    flts = floaters_for_district(associates, store.district)
    pool = local if local else (flts if flts else associates)
    return balance_load(tasks, pool, deadline)


def assignment_conflicts(assigned_tasks: list[dict], deadline: datetime | None = None) -> list[str]:
    """Check assigned tasks for missing associate_id or deadline violations."""
    issues: list[str] = []
    for t in assigned_tasks:
        if not t.get("associate_id"):
            issues.append(f"Task {t.get('task_id')} missing associate_id")
        w = t.get("window", [])
        if len(w) != 2:
            issues.append(f"Task {t.get('task_id')} invalid window")
        elif deadline is not None and not is_before_deadline(w[1], deadline):
            issues.append(f"Task {t.get('task_id')} window end {w[1]} not before deadline {deadline.isoformat()}")
    return issues


def assignment_summary(assigned_tasks: list[dict]) -> dict:
    """Summarize task counts per assigned associate."""
    by_assoc: dict[str, int] = {}
    for t in assigned_tasks:
        aid = str(t.get("associate_id", "UNASSIGNED"))
        by_assoc[aid] = by_assoc.get(aid, 0) + 1
    return {"total_tasks": len(assigned_tasks), "by_associate": by_assoc}


def assignment_to_records(assigned_tasks: list[dict]) -> list[dict]:
    """Return assigned task dicts ready for plan serialization."""
    return [dict(t) for t in assigned_tasks]
