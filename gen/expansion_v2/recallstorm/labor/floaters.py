"""District floater allocation and non-overlapping store windows."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
import math

from contract import Associate, HandoffKind, Store
from recallstorm.core.clock import iso_with_offset, window_overlaps
from recallstorm.core.ids import make_handoff_id


@dataclass
class FloaterPool:
    """Pool of district floater associates and their store dispatches."""

    floaters: list[Associate] = field(default_factory=list)
    dispatches: list[dict] = field(default_factory=list)


def floater_need(store_tasks_mins: float, store_assoc_mins: float) -> float:
    """Return extra labor minutes needed from district floaters."""
    return max(0.0, round(float(store_tasks_mins) - float(store_assoc_mins), 2))


def floater_travel_minutes(s1: Store, s2: Store) -> float:
    """Estimate travel time in minutes between two stores."""
    if s1.store_id == s2.store_id:
        return 0.0
    dist_deg = math.hypot(s1.lat - s2.lat, s1.lon - s2.lon)
    return round(max(10.0, dist_deg * 90.0), 1)


def dispatch_floater(
    floater: Associate,
    store_id: str,
    start: datetime,
    duration_mins: float,
    deadline: datetime | None = None,
) -> dict:
    """Create a floater dispatch record clamped to floater shift and scenario deadline."""
    s = max(start, floater.shift_start)
    e = min(floater.shift_end, s + timedelta(minutes=max(5.0, duration_mins)))
    if deadline is not None and e >= deadline:
        e = deadline - timedelta(minutes=1)
        if s >= e:
            s = e - timedelta(minutes=5)
    return {
        "associate_id": floater.associate_id,
        "district": floater.district,
        "store_id": store_id,
        "start": s,
        "end": e,
        "window": [iso_with_offset(s), iso_with_offset(e)],
        "duration_mins": round((e - s).total_seconds() / 60.0, 2),
    }


def floater_windows(dispatches: list[dict], associate_id: str) -> list[tuple[datetime, datetime]]:
    """Return (start, end) datetime tuples for all dispatches of associate_id."""
    out: list[tuple[datetime, datetime]] = []
    for d in dispatches:
        if d.get("associate_id") == associate_id:
            s = d["start"] if isinstance(d.get("start"), datetime) else datetime.fromisoformat(d["window"][0])
            e = d["end"] if isinstance(d.get("end"), datetime) else datetime.fromisoformat(d["window"][1])
            out.append((s, e))
    return sorted(out, key=lambda w: w[0])


def one_store_per_window(dispatches: list[dict]) -> bool:
    """Verify invariant: a floater is never assigned to two different stores during overlapping windows."""
    by_assoc: dict[str, list[dict]] = {}
    for d in dispatches:
        by_assoc.setdefault(str(d["associate_id"]), []).append(d)
    for _, items in by_assoc.items():
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                if items[i]["store_id"] == items[j]["store_id"]:
                    continue
                w1 = (
                    items[i]["start"] if isinstance(items[i].get("start"), datetime) else datetime.fromisoformat(items[i]["window"][0]),
                    items[i]["end"] if isinstance(items[i].get("end"), datetime) else datetime.fromisoformat(items[i]["window"][1]),
                )
                w2 = (
                    items[j]["start"] if isinstance(items[j].get("start"), datetime) else datetime.fromisoformat(items[j]["window"][0]),
                    items[j]["end"] if isinstance(items[j].get("end"), datetime) else datetime.fromisoformat(items[j]["window"][1]),
                )
                if window_overlaps(w1, w2):
                    return False
    return True


def floater_handoffs(dispatches: list[dict]) -> list[dict]:
    """Convert floater dispatches into plan.jsonl 'handoff' records of kind FLOATER."""
    out: list[dict] = []
    for idx, d in enumerate(dispatches):
        out.append(
            {
                "type": "handoff",
                "handoff_id": make_handoff_id(HandoffKind.FLOATER.value, d["associate_id"], d["store_id"], idx),
                "kind": HandoffKind.FLOATER.value,
                "from_id": d["associate_id"],
                "to_id": d["store_id"],
                "window": d["window"],
                "qty": 1,
                "ref_ids": list(d.get("task_ids", [])),
                "src": "recallstorm/labor/floaters.py",
            }
        )
    return out


def validate_floaters(dispatches: list[dict]) -> list[str]:
    """Validate floater dispatches for non-overlapping store windows."""
    if not one_store_per_window(dispatches):
        return ["Floater assigned to multiple stores in overlapping windows"]
    return []


def floater_plan_summary(dispatches: list[dict]) -> dict:
    """Summarize floater dispatches."""
    return {
        "dispatch_count": len(dispatches),
        "floaters_used": len({d["associate_id"] for d in dispatches}),
        "valid": one_store_per_window(dispatches),
    }
