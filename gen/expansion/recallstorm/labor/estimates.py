"""Task labor duration estimation model for shelf pulls, restocking, and signage."""
from __future__ import annotations

from dataclasses import dataclass
from contract import Action


@dataclass(frozen=True)
class EstimateModel:
    """Parameters for estimating in-store task durations."""

    base_pull_mins: float = 2.0
    per_unit_pull_mins: float = 0.1
    base_place_mins: float = 3.0
    tag_mins: float = 1.0


def pull_minutes(units: int) -> float:
    """Estimate minutes required to pull `units` from a shelf facing."""
    if units < 0:
        raise ValueError("units must be non-negative")
    return round(2.0 + 0.1 * units, 2)


def place_minutes(units: int) -> float:
    """Estimate minutes required to stock `units` of a substitute SKU."""
    if units < 0:
        raise ValueError("units must be non-negative")
    return round(3.0 + 0.12 * units, 2)


def tag_minutes(count: int = 1) -> float:
    """Estimate minutes required to print and hang `count` flash tags."""
    if count < 0:
        raise ValueError("count must be non-negative")
    return round(1.0 * count, 2)


def walk_minutes(dist_ft: float) -> float:
    """Estimate walking time in minutes at 240 feet/minute (4 ft/sec)."""
    if dist_ft < 0:
        raise ValueError("dist_ft must be non-negative")
    return round(dist_ft / 240.0, 2)


def task_minutes(action: Action | str, units: int = 10) -> float:
    """Estimate duration in minutes for a single shelf task."""
    act = action.value if isinstance(action, Action) else str(action).strip().upper()
    if act in (Action.PULL.value, Action.HOLD_VERIFY.value):
        return pull_minutes(units)
    if act == Action.PLACE_SUB.value:
        return place_minutes(units)
    if act == Action.TAG_FLASH.value:
        return tag_minutes(1)
    raise ValueError(f"Unknown action: {action}")


def minutes_by_action(tasks: list[dict]) -> dict[str, float]:
    """Sum estimated minutes grouped by task action."""
    totals: dict[str, float] = {}
    for t in tasks:
        act = str(t.get("action", Action.PULL.value))
        qty = int(t.get("qty_units", 1))
        totals[act] = round(totals.get(act, 0.0) + task_minutes(act, qty), 2)
    return totals


def store_minutes(tasks: list[dict]) -> float:
    """Compute total estimated labor minutes for all tasks in a store."""
    return round(sum(minutes_by_action(tasks).values()), 2)


def estimate_playbook(tasks: list[dict]) -> dict[str, float]:
    """Return playbook labor estimate breakdown."""
    by_act = minutes_by_action(tasks)
    return {**by_act, "total_minutes": round(sum(by_act.values()), 2)}
