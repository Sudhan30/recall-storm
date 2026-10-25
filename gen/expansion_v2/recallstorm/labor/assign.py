"""Assign shelf tasks to store associates and floaters within shift windows."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from contract import Action, Associate
from recallstorm.core.clock import iso_with_offset
from recallstorm.labor.estimates import task_minutes
from recallstorm.labor.shifts import shift_window


@dataclass
class LaborPlan:
    """Assigned shelf tasks and associate workload summary."""

    tasks: list[dict] = field(default_factory=list)


def greedy_assign(
    tasks: list[dict], associates: list[Associate], deadline: datetime | None = None
) -> list[dict]:
    """Assign tasks in sequence across available associates, clamping windows strictly before deadline."""
    if not tasks:
        return []
    if not associates:
        fallback_start = (deadline - timedelta(hours=4)) if deadline else datetime.fromisoformat("2026-12-30T22:00:00-08:00")
        fallback_end = (deadline - timedelta(minutes=5)) if deadline else (fallback_start + timedelta(minutes=30))
        win = [iso_with_offset(fallback_start), iso_with_offset(fallback_end)]
        return [{**t, "associate_id": t.get("associate_id") or "UNASSIGNED", "window": t.get("window") or win} for t in tasks]

    ordered_assocs = sorted(associates, key=lambda a: (a.is_floater, a.associate_id))
    cursors: dict[str, datetime] = {}
    bounds: dict[str, tuple[datetime, datetime]] = {}
    for a in ordered_assocs:
        s, e = shift_window(a, deadline=deadline)
        cursors[a.associate_id] = s
        bounds[a.associate_id] = (s, e)

    out: list[dict] = []
    for idx, t in enumerate(tasks):
        assoc = ordered_assocs[idx % len(ordered_assocs)]
        aid = assoc.associate_id
        s_bound, e_bound = bounds[aid]
        cur = cursors[aid]
        act = Action(str(t.get("action", "PULL")).upper())
        dur = max(1.0, task_minutes(act, int(t.get("qty_units", 1))))
        end_t = cur + timedelta(minutes=dur)
        if end_t > e_bound:
            end_t = e_bound
            cur = max(s_bound, end_t - timedelta(minutes=min(dur, 5.0)))
        else:
            cursors[aid] = end_t
        updated = dict(t)
        updated["associate_id"] = aid
        updated["window"] = [iso_with_offset(cur), iso_with_offset(end_t)]
        out.append(updated)
    return out


def assign_tasks(
    tasks: list[dict], associates: list[Associate], deadline: datetime | None = None
) -> list[dict]:
    """Assign tasks per store using store associates first, then district floaters."""
    by_store: dict[str, list[dict]] = {}
    for t in tasks:
        by_store.setdefault(str(t.get("store_id", "")), []).append(t)

    out: list[dict] = []
    for st_id in sorted(by_store.keys()):
        st_tasks = by_store[st_id]
        st_assocs = [a for a in associates if a.store_id == st_id and not a.is_floater]
        if not st_assocs:
            st_assocs = [a for a in associates if a.is_floater]
        if not st_assocs and associates:
            st_assocs = [associates[0]]
        out.extend(greedy_assign(st_tasks, st_assocs, deadline=deadline))
    return out


def balance_load(
    tasks: list[dict], associates: list[Associate], deadline: datetime | None = None
) -> dict[str, list[dict]]:
    """Assign tasks and group them by associate_id."""
    assigned = assign_tasks(tasks, associates, deadline=deadline)
    grouped: dict[str, list[dict]] = {}
    for t in assigned:
        grouped.setdefault(str(t["associate_id"]), []).append(t)
    return grouped


def assign_floaters(
    unassigned_tasks: list[dict], floaters: list[Associate], deadline: datetime | None = None
) -> list[dict]:
    """Assign overflow tasks to floater associates ensuring one store per floater window."""
    if not unassigned_tasks or not floaters:
        return unassigned_tasks
    return greedy_assign(unassigned_tasks, floaters, deadline=deadline)


def reassign_overflow(
    tasks: list[dict],
    associates: list[Associate],
    floaters: list[Associate],
    deadline: datetime | None = None,
) -> list[dict]:
    """Assign tasks across combined store associates and floaters."""
    return assign_tasks(tasks, associates + floaters, deadline=deadline)


def assignment_conflicts(tasks: list[dict]) -> list[str]:
    """Check assigned tasks for missing associate_id or invalid windows."""
    issues: list[str] = []
    for t in tasks:
        if not t.get("associate_id") or t.get("associate_id") == "UNASSIGNED":
            issues.append(f"Task {t.get('task_id')} is unassigned")
        win = t.get("window") or []
        if len(win) != 2 or win[1] < win[0]:
            issues.append(f"Task {t.get('task_id')} has invalid window {win}")
    return issues


def assignment_summary(tasks: list[dict]) -> dict:
    """Summarize task counts per associate."""
    by_assoc: dict[str, int] = {}
    for t in tasks:
        aid = str(t.get("associate_id", "UNASSIGNED"))
        by_assoc[aid] = by_assoc.get(aid, 0) + 1
    return {"total_tasks": len(tasks), "by_associate": by_assoc}


def assignment_to_records(tasks: list[dict]) -> list[dict]:
    """Return tasks formatted with provenance for plan.jsonl."""
    return [{**t, "src": t.get("src", "recallstorm/labor/assign.py")} for t in tasks]
