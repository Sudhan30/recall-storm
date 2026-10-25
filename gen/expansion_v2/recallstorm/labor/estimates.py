"""Time estimates for PULL, PLACE_SUB, TAG_FLASH, HOLD_VERIFY, and walking."""
from __future__ import annotations

from dataclasses import dataclass

from contract import Action


@dataclass(frozen=True)
class EstimateModel:
    """Parameters for shelf task duration estimation."""

    base_pull_mins: float = 2.0
    per_unit_pull_mins: float = 0.1
    base_place_mins: float = 2.0
    per_unit_place_mins: float = 0.12
    tag_mins: float = 1.0
    verify_mins: float = 3.0


def pull_minutes(units: int) -> float:
    """Estimate minutes required to pull units from a shelf facing."""
    if units < 0:
        raise ValueError("units must be non-negative")
    return round(2.0 + units * 0.1, 2)


def place_minutes(units: int) -> float:
    """Estimate minutes required to place substitute units onto a shelf facing."""
    if units < 0:
        raise ValueError("units must be non-negative")
    return round(2.0 + units * 0.12, 2)


def tag_minutes(facings_count: int = 1) -> float:
    """Estimate minutes required to flash/place shelf tags."""
    if facings_count < 0:
        raise ValueError("facings_count must be non-negative")
    return round(max(1, facings_count) * 1.0, 2)


def walk_minutes(distance_m: float, speed_mps: float = 1.2) -> float:
    """Estimate walking time in minutes for distance_m at speed_mps."""
    if distance_m < 0 or speed_mps <= 0:
        raise ValueError("Invalid distance or speed")
    return round((distance_m / speed_mps) / 60.0, 2)


def task_minutes(action: Action, units: int) -> float:
    """Return estimated duration in minutes for an Action and unit count."""
    if not isinstance(action, Action):
        action = Action(str(action).upper())
    if action == Action.PULL:
        return pull_minutes(units)
    if action == Action.PLACE_SUB:
        return place_minutes(units)
    if action == Action.TAG_FLASH:
        return tag_minutes(1)
    return 3.0


def minutes_by_action(tasks: list[dict]) -> dict[str, float]:
    """Sum estimated minutes grouped by task action."""
    out = {a.value: 0.0 for a in Action}
    for t in tasks:
        act = Action(str(t.get("action", "PULL")).upper())
        units = int(t.get("qty_units", 0))
        out[act.value] = round(out.get(act.value, 0.0) + task_minutes(act, units), 2)
    return out


def store_minutes(tasks: list[dict]) -> float:
    """Return total estimated minutes across all tasks in a store."""
    return round(sum(minutes_by_action(tasks).values()), 2)


def estimate_playbook(tasks: list[dict]) -> dict[str, float]:
    """Return a playbook timing estimate breakdown."""
    by_act = minutes_by_action(tasks)
    by_act["total"] = round(sum(by_act.values()), 2)
    return by_act
