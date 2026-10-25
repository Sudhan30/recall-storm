"""Store priority scoring and deterministic tie-breaking by store_id."""
from __future__ import annotations

from dataclasses import dataclass
from contract import Store, StoreFormat
from recallstorm.store.formats import format_priority


@dataclass(frozen=True)
class PriorityModel:
    """Weights for store priority scoring."""

    format_factor: float = 10.0
    demand_factor: float = 1.0


def format_weight(fmt: StoreFormat | str) -> float:
    """Return priority weight for a StoreFormat (higher is more urgent)."""
    rank = format_priority(fmt)
    return float(5 - rank)


def distance_weight(lat: float, lon: float) -> float:
    """Return a small deterministic geographic weight in [0.0, 1.0]."""
    return round((abs(lat) + abs(lon)) / 360.0, 4)


def deadline_weight(hours_left: float) -> float:
    """Return urgency weight inversely proportional to hours remaining until deadline."""
    if hours_left <= 0:
        return 10.0
    return round(min(10.0, 24.0 / hours_left), 3)


def store_priority(store: Store) -> float:
    """Compute baseline priority score for a Store."""
    if not isinstance(store, Store):
        raise TypeError("store must be a Store")
    return round(format_weight(store.format) * 10.0 + distance_weight(store.lat, store.lon), 4)


def priority_score(store: Store, demand_cases: int = 1) -> float:
    """Compute combined priority score for a store and its requested cases."""
    return round(store_priority(store) + max(0, demand_cases), 4)


def tie_break_key(store: Store) -> tuple[str, str]:
    """Return deterministic tie-break key (dc_id, store_id)."""
    return (store.dc_id, store.store_id)


def rank_stores(stores: list[Store]) -> list[Store]:
    """Rank stores deterministically by store_id (as required by contract tie-breaking)."""
    return sorted(stores, key=lambda s: s.store_id)


def priority_report(stores: list[Store]) -> dict:
    """Return a summary report of store priorities."""
    ranked = rank_stores(stores)
    return {
        "store_count": len(ranked),
        "ordered_ids": [s.store_id for s in ranked],
    }
