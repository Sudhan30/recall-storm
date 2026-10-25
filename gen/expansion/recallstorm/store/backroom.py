"""Store backroom locations, topstock estimation, and return quarantine staging."""
from __future__ import annotations

from dataclasses import dataclass, field
from contract import Action, Facing, Location, Store, StoreFormat
from recallstorm.core.ids import make_task_id


@dataclass
class Backroom:
    """State of a store's backroom staging bays."""

    store_id: str
    staged_cases: dict[str, int] = field(default_factory=dict)


def staging_area(store_id: str) -> Location:
    """Return the canonical backroom quarantine staging Location for a store."""
    if not isinstance(store_id, str) or not store_id.strip():
        raise ValueError("store_id must be non-empty")
    return Location(aisle="BACKROOM", bay=1, shelf=1, pos=1)


def backroom_locations(store_id: str) -> list[Location]:
    """Return standard backroom receiving and quarantine staging locations."""
    if not isinstance(store_id, str) or not store_id.strip():
        raise ValueError("store_id must be non-empty")
    return [Location(aisle="BACKROOM", bay=b, shelf=1, pos=1) for b in (1, 2, 3, 4)]


def backroom_stock(facings: list[Facing], store_id: str) -> dict[str, int]:
    """Estimate backroom buffer units per SKU (25% of salesfloor units) for store_id."""
    out: dict[str, int] = {}
    for f in facings:
        if f.store_id == store_id:
            out[f.sku_id] = out.get(f.sku_id, 0) + max(1, f.units // 4)
    return out


def topstock_for_sku(facings: list[Facing], store_id: str, sku_id: str) -> int:
    """Estimate topstock overflow units above the aisle for a SKU."""
    salesfloor = sum(f.units for f in facings if f.store_id == store_id and f.sku_id == sku_id)
    return salesfloor // 2 if salesfloor > 0 else 0


def backroom_pull_task(store_id: str, sku_id: str, units: int, seq: int = 99) -> dict:
    """Create a backroom pull task dictionary."""
    if units <= 0:
        raise ValueError("units must be positive")
    loc = staging_area(store_id)
    return {
        "task_id": make_task_id(store_id, sku_id, Action.PULL, seq),
        "store_id": store_id,
        "sku_id": sku_id,
        "action": Action.PULL.value,
        "loc": {"aisle": loc.aisle, "bay": loc.bay, "shelf": loc.shelf, "pos": loc.pos},
        "qty_units": units,
    }


def backroom_capacity_left(store: Store, staged_cases: int) -> int:
    """Return remaining backroom staging capacity in cases for a Store."""
    max_cap = 500 if store.format == StoreFormat.SAMS else (300 if store.format == StoreFormat.SUPERCENTER else 150)
    return max(0, max_cap - max(0, staged_cases))


def stage_returns(store_id: str, cases_by_sku: dict[str, int]) -> dict:
    """Stage pulled return cases in the store's backroom quarantine area."""
    total = sum(v for v in cases_by_sku.values() if v > 0)
    return {
        "store_id": store_id,
        "staging_loc": staging_area(store_id),
        "total_cases": total,
        "by_sku": {k: v for k, v in cases_by_sku.items() if v > 0},
    }


def backroom_summary(store_id: str, staged: dict[str, int]) -> dict:
    """Summarize backroom quarantine staging for a store."""
    return {
        "store_id": store_id,
        "sku_count": len(staged),
        "total_cases": sum(staged.values()),
    }
