"""Deadline guard ensuring every task, playbook, and handoff window ends strictly before scenario deadline."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from recallstorm.core.clock import is_before_deadline, iso_with_offset, minutes_between


@dataclass(frozen=True)
class DeadlineGuard:
    """Enforces scenario deadline across plan windows."""

    deadline: datetime


def deadline_for_plan(deadline_dt: datetime | str, tz_name: str = "America/Los_Angeles") -> str:
    """Format the plan deadline as an ISO 8601 string with UTC offset."""
    dt = datetime.fromisoformat(deadline_dt) if isinstance(deadline_dt, str) else deadline_dt
    return iso_with_offset(dt, tz_name)


def window_before_deadline(window: list[str] | tuple[str, str], deadline_dt: datetime | str) -> bool:
    """Return True if window start <= end and end < deadline_dt."""
    if not isinstance(window, (list, tuple)) or len(window) != 2:
        return False
    s = datetime.fromisoformat(window[0])
    e = datetime.fromisoformat(window[1])
    if e < s:
        return False
    return is_before_deadline(e, deadline_dt)


def shrink_window(start_dt: datetime, end_dt: datetime, deadline_dt: datetime) -> tuple[datetime, datetime]:
    """Clamp (start_dt, end_dt) so that end_dt is strictly before deadline_dt."""
    safe_end = deadline_dt - timedelta(minutes=1)
    clamped_e = min(end_dt, safe_end)
    clamped_s = min(start_dt, clamped_e - timedelta(minutes=5))
    return clamped_s, clamped_e


def deadline_slack_minutes(window: list[str] | tuple[str, str], deadline_dt: datetime | str) -> float:
    """Return minutes between window end and deadline_dt (positive = before deadline)."""
    if len(window) != 2:
        raise ValueError("window must have length 2")
    return minutes_between(window[1], deadline_dt)


def late_risk(window: list[str] | tuple[str, str], deadline_dt: datetime | str) -> float:
    """Return a late-risk score in [0.0, 1.0] based on slack before deadline."""
    slack = deadline_slack_minutes(window, deadline_dt)
    if slack <= 0:
        return 1.0
    if slack >= 120.0:
        return 0.0
    return round(1.0 - (slack / 120.0), 3)


def enforce_deadline(
    records: list[dict],
    deadline_dt: datetime | str,
    tz_name: str = "America/Los_Angeles",
) -> list[dict]:
    """Clamp any late windows in shelf_task, handoff, or store_playbook records to end before deadline_dt."""
    dl = datetime.fromisoformat(deadline_dt) if isinstance(deadline_dt, str) else deadline_dt
    out: list[dict] = []
    for r in records:
        rec = dict(r)
        if "window" in rec and isinstance(rec["window"], list) and len(rec["window"]) == 2:
            if not window_before_deadline(rec["window"], dl):
                s = datetime.fromisoformat(rec["window"][0])
                e = datetime.fromisoformat(rec["window"][1])
                ns, ne = shrink_window(s, e, dl)
                rec["window"] = [iso_with_offset(ns, tz_name), iso_with_offset(ne, tz_name)]
        if "windows" in rec and isinstance(rec["windows"], list):
            new_wins: list[list[str]] = []
            for w in rec["windows"]:
                if isinstance(w, list) and len(w) == 2 and not window_before_deadline(w, dl):
                    s = datetime.fromisoformat(w[0])
                    e = datetime.fromisoformat(w[1])
                    ns, ne = shrink_window(s, e, dl)
                    new_wins.append([iso_with_offset(ns, tz_name), iso_with_offset(ne, tz_name)])
                else:
                    new_wins.append(w)
            rec["windows"] = new_wins
        out.append(rec)
    return out


def deadline_violations(records: list[dict], deadline_dt: datetime | str) -> list[str]:
    """Return a list of violation descriptions for any windows not ending strictly before deadline_dt."""
    issues: list[str] = []
    for r in records:
        rtype = r.get("type", "record")
        if "window" in r and not window_before_deadline(r["window"], deadline_dt):
            issues.append(f"{rtype} window {r.get('window')} violates deadline {deadline_dt}")
        for w in r.get("windows", []):
            if not window_before_deadline(w, deadline_dt):
                issues.append(f"{rtype} windows entry {w} violates deadline {deadline_dt}")
    return issues


def deadline_report(records: list[dict], deadline_dt: datetime | str) -> dict:
    """Summarize deadline compliance across plan records."""
    viols = deadline_violations(records, deadline_dt)
    return {"compliant": len(viols) == 0, "violation_count": len(viols), "violations": viols}
