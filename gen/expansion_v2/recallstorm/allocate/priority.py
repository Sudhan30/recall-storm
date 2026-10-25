"""Store priority ranking and deterministic tie-breaking by store_id."""
from __future__ import annotations

from dataclasses import dataclass

from contract import Store, StoreFormat
from recallstorm.store.formats import format_priority


@dataclass(frozen=True)
class PriorityModel:
    """Weights for store substitute allocation priority."""

    format_factor: float = 10.0
    demand_factor: float = 1.0


def tie_break_key(store_id: str) -> str:
    """Return canonical lexicographic tie-break key for store_id."""
    return str(store_id).strip()


def format_weight(fmt: StoreFormat) -> float:
    """Return priority weight for a StoreFormat (higher = higher priority)."""
    return float(5 - format_priority(fmt))


def distance_weight(lat: float, lon: float) -> float:
    """Return a normalized geographic weight in [0.0, 1.0]."""
    return round(min(1.0, max(0.0, (abs(lat) + abs(lon)) / 300.0)), 4)


def deadline_weight(hours_left: float = 24.0) -> float:
    """Return urgency weight inversely proportional to hours_left."""
    return round(100.0 / max(1.0, float(hours_left)), 2)


def store_priority(store: Store) -> float:
    """Compute baseline priority score for a Store."""
    return round(format_weight(store.format) * 10.0, 2)


def priority_score(store: Store, demand_cases: int = 1) -> float:
    """Compute composite priority score for store and demand_cases."""
    return round(store_priority(store) + max(0, int(demand_cases)), 2)


def rank_stores(stores: list[Store]) -> list[Store]:
    """Order stores deterministically by store_id (contract tie-break rule)."""
    return sorted(stores, key=lambda s: tie_break_key(s.store_id))


def priority_report(stores: list[Store]) -> dict:
    """Summarize store priorities."""
    ranked = rank_stores(stores)
    return {
        "store_count": len(ranked),
        "ordered_ids": [s.store_id for s in ranked],
    }
