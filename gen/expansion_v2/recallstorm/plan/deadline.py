"""Enforce scenario deadline across all task, playbook, and handoff windows."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from recallstorm.core.clock import is_before_deadline, iso_with_offset, minutes_between, to_local


@dataclass(frozen=True)
class DeadlineGuard:
    """Guard verifying that every operational window ends strictly before deadline."""

    deadline: datetime


def deadline_for_plan(deadline_iso: str, tz_name: str = "America/Los_Angeles") -> datetime:
    """Parse an ISO deadline string into a timezone-aware datetime."""
    dt = datetime.fromisoformat(deadline_iso)
    return to_local(dt, tz_name)


def window_before_deadline(window: list[str] | tuple[str, str], deadline: datetime) -> bool:
    """Return True if window = [start_iso, end_iso] has start <= end < deadline."""
    if not window or len(window) != 2:
        return False
    s = datetime.fromisoformat(window[0])
    e = datetime.fromisoformat(window[1])
    if e < s:
        return False
    return is_before_deadline(e, deadline, strict=True)


def shrink_window(window: tuple[datetime, datetime], deadline: datetime) -> tuple[datetime, datetime]:
    """Clamp a (start, end) datetime window so that end is strictly before deadline."""
    s, e = window
    safe_end = deadline - timedelta(minutes=1)
    if e >= deadline:
        e = safe_end
    if s >= e:
        s = e - timedelta(minutes=5)
    return (s, e)


def deadline_slack_minutes(window: tuple[datetime, datetime], deadline: datetime) -> float:
    """Return minutes between window[1] and deadline."""
    return round(minutes_between(window[1], deadline), 2)


def late_risk(window: tuple[datetime, datetime], deadline: datetime) -> float:
    """Return a lateness risk score in [0.0, 1.0] based on slack before deadline."""
    slack = deadline_slack_minutes(window, deadline)
    if slack <= 0:
        return 1.0
    if slack >= 120.0:
        return 0.0
    return round(1.0 - (slack / 120.0), 3)


def enforce_deadline(records: list[dict], deadline: datetime) -> list[dict]:
    """Clamp all task, handoff, and playbook windows in records to end strictly before deadline."""
    out: list[dict] = []
    for rec in records:
        r = dict(rec)
        if "window" in r and isinstance(r["window"], list) and len(r["window"]) == 2:
            s, e = shrink_window(
                (datetime.fromisoformat(r["window"][0]), datetime.fromisoformat(r["window"][1])),
                deadline,
            )
            r["window"] = [iso_with_offset(s), iso_with_offset(e)]
        if "windows" in r and isinstance(r["windows"], list):
            new_wins: list[list[str]] = []
            for w in r["windows"]:
                if isinstance(w, list) and len(w) == 2:
                    s, e = shrink_window((datetime.fromisoformat(w[0]), datetime.fromisoformat(w[1])), deadline)
                    new_wins.append([iso_with_offset(s), iso_with_offset(e)])
            r["windows"] = new_wins
        out.append(r)
    return out


def deadline_violations(records: list[dict], deadline: datetime) -> list[str]:
    """Return diagnostic strings for any window in records that ends at or after deadline."""
    viols: list[str] = []
    for r in records:
        rtype = r.get("type", "record")
        if "window" in r and isinstance(r["window"], list):
            if not window_before_deadline(r["window"], deadline):
                viols.append(f"{rtype} {r.get('task_id') or r.get('handoff_id')} violates deadline: {r['window']}")
        if "windows" in r and isinstance(r["windows"], list):
            for w in r["windows"]:
                if not window_before_deadline(w, deadline):
                    viols.append(f"{rtype} {r.get('store_id')} violates deadline: {w}")
    return viols


def deadline_report(records: list[dict], deadline: datetime) -> dict:
    """Summarize deadline compliance across plan records."""
    viols = deadline_violations(records, deadline)
    return {"deadline": iso_with_offset(deadline), "violation_count": len(viols), "violations": viols}
