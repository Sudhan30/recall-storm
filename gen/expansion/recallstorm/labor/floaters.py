"""District floater dispatching with strict one-store-per-window invariant."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime
from contract import Associate, HandoffKind, Store
from recallstorm.core.clock import window_overlaps
from recallstorm.core.ids import make_handoff_id


@dataclass
class FloaterPool:
    """District pool of floater associates and their dispatches."""

    district: str
    floaters: list[Associate] = field(default_factory=list)
    dispatches: list[dict] = field(default_factory=list)


def floater_need(store_minutes_needed: float, local_capacity_mins: float) -> float:
    """Return overflow labor minutes requiring floater support."""
    return max(0.0, store_minutes_needed - local_capacity_mins)


def floater_travel_minutes(s1: Store, s2: Store) -> float:
    """Estimate travel time in minutes between two stores from lat/lon."""
    dist_deg = math.hypot(s1.lat - s2.lat, s1.lon - s2.lon)
    miles = dist_deg * 60.0
    return round(max(10.0, miles * 1.5), 1)


def dispatch_floater(
    floater: Associate,
    store_id: str,
    window: list[str] | tuple[str, str],
    task_ids: list[str] | None = None,
) -> dict:
    """Create a floater dispatch record for a store and time window."""
    if not isinstance(floater, Associate) or not floater.is_floater:
        raise ValueError("floater must be an Associate with is_floater=True")
    if len(window) != 2:
        raise ValueError("window must have [start, end]")
    return {
        "associate_id": floater.associate_id,
        "district": floater.district,
        "store_id": store_id,
        "window": [str(window[0]), str(window[1])],
        "task_ids": list(task_ids) if task_ids else [],
    }


def floater_windows(dispatches: list[dict]) -> dict[str, list[tuple[str, datetime, datetime]]]:
    """Group dispatched (store_id, start, end) intervals by floater associate_id."""
    out: dict[str, list[tuple[str, datetime, datetime]]] = {}
    for d in dispatches:
        aid = str(d["associate_id"])
        w = d["window"]
        s = datetime.fromisoformat(w[0])
        e = datetime.fromisoformat(w[1])
        out.setdefault(aid, []).append((str(d["store_id"]), s, e))
    return out


def one_store_per_window(dispatches: list[dict]) -> bool:
    """Verify that no floater is assigned to two different stores during overlapping windows."""
    by_floater = floater_windows(dispatches)
    for intervals in by_floater.values():
        for i in range(len(intervals)):
            for j in range(i + 1, len(intervals)):
                st1, s1, e1 = intervals[i]
                st2, s2, e2 = intervals[j]
                if st1 != st2 and window_overlaps((s1, e1), (s2, e2)):
                    return False
    return True


def validate_floaters(dispatches: list[dict]) -> list[str]:
    """Validate floater dispatches and return any overlapping-window conflicts."""
    issues: list[str] = []
    if not one_store_per_window(dispatches):
        issues.append("Floater assigned to multiple stores in overlapping windows")
    return issues


def floater_handoffs(dispatches: list[dict]) -> list[dict]:
    """Convert floater dispatches into FLOATER handoff dictionaries."""
    out: list[dict] = []
    for idx, d in enumerate(dispatches):
        hid = make_handoff_id(HandoffKind.FLOATER, d["associate_id"], d["store_id"], idx)
        out.append(
            {
                "handoff_id": hid,
                "kind": HandoffKind.FLOATER.value,
                "from_id": d["associate_id"],
                "to_id": d["store_id"],
                "window": list(d["window"]),
                "qty": max(1, len(d.get("task_ids", []))),
                "ref_ids": list(d.get("task_ids", [])),
            }
        )
    return out


def floater_plan_summary(dispatches: list[dict]) -> dict:
    """Summarize floater dispatches."""
    return {
        "dispatch_count": len(dispatches),
        "floaters_used": len({d["associate_id"] for d in dispatches}),
        "valid": one_store_per_window(dispatches),
    }
