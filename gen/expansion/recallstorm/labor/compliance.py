"""State labor compliance rules: shift caps, meal breaks, and overtime checks."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from contract import Associate
from recallstorm.core.clock import minutes_between


@dataclass(frozen=True)
class LaborRules:
    """Shift compliance parameters."""

    state: str = "CA"
    max_mins: int = 480
    meal_threshold_mins: int = 300


def max_shift_minutes(state: str = "CA") -> int:
    """Return maximum regular shift minutes before overtime (480 mins = 8 hours)."""
    if not isinstance(state, str) or not state.strip():
        raise ValueError("state must be a non-empty string")
    return 480


def break_required(shift_mins: float) -> bool:
    """Return True if a meal break is required (shift > 300 minutes / 5 hours)."""
    if shift_mins < 0:
        raise ValueError("shift_mins must be non-negative")
    return shift_mins > 300.0


def meal_break_window(shift_start: datetime, shift_end: datetime) -> tuple[datetime, datetime]:
    """Return a 30-minute meal break window at the midpoint of a shift."""
    if shift_end <= shift_start:
        raise ValueError("shift_end must be after shift_start")
    mid = shift_start + (shift_end - shift_start) / 2
    return mid, min(shift_end, mid + timedelta(minutes=30))


def overtime_minutes(worked_mins: float, state: str = "CA") -> float:
    """Return minutes worked beyond the regular shift cap."""
    if worked_mins < 0:
        raise ValueError("worked_mins must be non-negative")
    cap = float(max_shift_minutes(state))
    return max(0.0, worked_mins - cap)


def check_labor_rules(assoc: Associate, assigned_mins: float) -> list[str]:
    """Check if assigned_mins exceeds the associate's shift length or regular cap."""
    if not isinstance(assoc, Associate):
        raise TypeError("assoc must be an Associate")
    issues: list[str] = []
    shift_len = minutes_between(assoc.shift_start, assoc.shift_end)
    if assigned_mins > shift_len:
        issues.append(f"Assigned {assigned_mins:.1f}m exceeds shift duration {shift_len:.1f}m for {assoc.associate_id}")
    if overtime_minutes(assigned_mins) > 0:
        issues.append(f"Overtime required for {assoc.associate_id}: {assigned_mins:.1f}m")
    return issues


def labor_violations(associates: list[Associate], assigned_by_id: dict[str, float]) -> list[dict]:
    """Collect labor compliance violations across a roster of associates."""
    out: list[dict] = []
    for a in associates:
        used = assigned_by_id.get(a.associate_id, 0.0)
        for msg in check_labor_rules(a, used):
            out.append({"associate_id": a.associate_id, "store_id": a.store_id, "message": msg})
    return out


def violation_to_record(v: dict) -> dict:
    """Normalize a labor violation dictionary."""
    return dict(v)


def labor_report(associates: list[Associate], assigned_by_id: dict[str, float]) -> dict:
    """Generate a summary report of associate utilization and labor compliance."""
    violations = labor_violations(associates, assigned_by_id)
    return {
        "associate_count": len(associates),
        "total_assigned_minutes": round(sum(assigned_by_id.values()), 2),
        "violation_count": len(violations),
        "violations": violations,
    }
