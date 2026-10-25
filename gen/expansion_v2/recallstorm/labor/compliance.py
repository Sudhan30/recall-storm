"""Labor shift limits, meal breaks, and overtime compliance."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from contract import Associate
from recallstorm.core.clock import minutes_between


@dataclass(frozen=True)
class LaborRules:
    """Statutory and corporate shift compliance thresholds."""

    max_shift_mins: float = 480.0
    break_threshold_mins: float = 300.0
    meal_duration_mins: float = 30.0


def max_shift_minutes(is_floater: bool = False) -> float:
    """Return maximum allowed shift work minutes."""
    return 450.0 if is_floater else 480.0


def break_required(shift_mins: float) -> bool:
    """Return True if a shift of shift_mins requires a meal break (> 300 mins / 5 hours)."""
    return float(shift_mins) > 300.0


def meal_break_window(assoc: Associate) -> tuple[datetime, datetime] | None:
    """Return a 30-minute mid-shift meal break window if break_required, else None."""
    dur = minutes_between(assoc.shift_start, assoc.shift_end)
    if not break_required(dur):
        return None
    mid = assoc.shift_start + timedelta(minutes=dur / 2.0 - 15.0)
    return (mid, mid + timedelta(minutes=30))


def overtime_minutes(worked_mins: float, standard_mins: float = 480.0) -> float:
    """Return minutes worked in excess of standard_mins."""
    return max(0.0, float(worked_mins) - float(standard_mins))


def check_labor_rules(assoc: Associate, assigned_mins: float) -> list[str]:
    """Return compliance issue strings if assigned_mins exceeds assoc's shift capacity."""
    issues: list[str] = []
    shift_dur = minutes_between(assoc.shift_start, assoc.shift_end)
    cap = min(shift_dur, max_shift_minutes(assoc.is_floater))
    if assigned_mins > cap:
        issues.append(f"Associate {assoc.associate_id} assigned {assigned_mins:.1f}m > capacity {cap:.1f}m")
    return issues


def labor_violations(associates: list[Associate], load_by_assoc: dict[str, float]) -> list[dict]:
    """Find all labor compliance violations across associates."""
    out: list[dict] = []
    for a in associates:
        used = load_by_assoc.get(a.associate_id, 0.0)
        for msg in check_labor_rules(a, used):
            out.append({"associate_id": a.associate_id, "assigned_mins": used, "violation": msg})
    return out


def violation_to_record(v: dict) -> dict:
    """Attach source provenance to a labor violation record."""
    return {**v, "src": "recallstorm/labor/compliance.py"}


def labor_report(associates: list[Associate], load_by_assoc: dict[str, float]) -> dict:
    """Summarize associate labor utilization and compliance."""
    viols = labor_violations(associates, load_by_assoc)
    return {
        "associate_count": len(associates),
        "total_assigned_mins": round(sum(load_by_assoc.values()), 2),
        "violation_count": len(viols),
        "violations": viols,
    }
