"""Backroom stock locations, staging areas, and pull tasks."""
from __future__ import annotations

from dataclasses import dataclass

from contract import Action, Facing, Location
from recallstorm.core.ids import make_task_id


@dataclass
class Backroom:
    """Store backroom state and return staging capacity."""

    store_id: str
    max_cases: int = 500
    staged_cases: int = 0


def staging_area(store_id: str) -> Location:
    """Return the canonical backroom quarantine/staging Location for a store."""
    if not isinstance(store_id, str) or not store_id.strip():
        raise ValueError("store_id must be non-empty")
    return Location(aisle="BACKROOM", bay=1, shelf=1, pos=1)


def backroom_locations(store_id: str) -> list[Location]:
    """Return standard backroom receiving and quarantine Locations for store_id."""
    if not isinstance(store_id, str) or not store_id.strip():
        raise ValueError("store_id must be non-empty")
    return [Location(aisle="BACKROOM", bay=b, shelf=1, pos=1) for b in (1, 2, 3, 4)]


def backroom_stock(store_id: str, sku_id: str, units: int = 0) -> dict:
    """Build a backroom stock record for store_id and sku_id."""
    if units < 0:
        raise ValueError("units cannot be negative")
    return {"store_id": store_id, "sku_id": sku_id, "loc": staging_area(store_id), "units": units}


def topstock_for_sku(facings: list[Facing], sku_id: str) -> list[Location]:
    """Return topstock Locations (shelf=99) above each salesfloor facing of sku_id."""
    return [
        Location(aisle=f.loc.aisle, bay=f.loc.bay, shelf=99, pos=f.loc.pos)
        for f in facings
        if f.sku_id == sku_id
    ]


def backroom_pull_task(store_id: str, sku_id: str, units: int) -> dict:
    """Construct a backroom pull task dictionary."""
    if units < 0:
        raise ValueError("units must be non-negative")
    loc = staging_area(store_id)
    return {
        "task_id": make_task_id(store_id, sku_id, Action.PULL.value, 900),
        "store_id": store_id,
        "sku_id": sku_id,
        "action": Action.PULL.value,
        "loc": {"aisle": loc.aisle, "bay": loc.bay, "shelf": loc.shelf, "pos": loc.pos},
        "qty_units": units,
    }


def backroom_capacity_left(current_cases: int, max_cases: int = 500) -> int:
    """Return remaining case staging capacity in the backroom."""
    return max(0, max_cases - max(0, current_cases))


def stage_returns(store_id: str, cases: int) -> dict:
    """Stage pulled cases in the store's backroom quarantine area."""
    if cases < 0:
        raise ValueError("cases cannot be negative")
    return {"store_id": store_id, "staged_cases": cases, "staging_loc": staging_area(store_id)}


def backroom_summary(store_id: str, staged_cases: int) -> dict:
    """Summarize backroom staging utilization."""
    return {
        "store_id": store_id,
        "staged_cases": staged_cases,
        "capacity_left": backroom_capacity_left(staged_cases),
    }
