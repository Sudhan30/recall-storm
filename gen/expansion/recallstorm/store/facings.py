"""Shelf facing queries, affected unit counts, and aisle groupings."""
from __future__ import annotations

from contract import Facing, Location, SkuDecision, Verdict


def facing_key(facing: Facing) -> tuple[str, str, int, int, int]:
    """Return a deterministic sort key for a Facing."""
    return (facing.store_id, facing.loc.aisle, facing.loc.bay, facing.loc.shelf, facing.loc.pos)


def facings_for_store(facings: list[Facing], store_id: str) -> list[Facing]:
    """Return all facings belonging to store_id sorted by location."""
    matched = [f for f in facings if f.store_id == store_id]
    return sorted(matched, key=facing_key)


def facings_for_sku(facings: list[Facing], sku_id: str) -> list[Facing]:
    """Return all facings carrying sku_id across all stores."""
    return sorted([f for f in facings if f.sku_id == sku_id], key=facing_key)


def affected_facings(
    facings: list[Facing],
    decisions: dict[str, SkuDecision] | list[SkuDecision],
) -> list[Facing]:
    """Return facings whose SKU verdict is PULL or HOLD_VERIFY."""
    dmap = decisions if isinstance(decisions, dict) else {d.sku_id: d for d in decisions}
    affected_ids = {
        sku_id for sku_id, dec in dmap.items()
        if dec.verdict in (Verdict.PULL, Verdict.HOLD_VERIFY)
    }
    return sorted([f for f in facings if f.sku_id in affected_ids], key=facing_key)


def units_on_shelf(facings: list[Facing], store_id: str, sku_id: str | None = None) -> int:
    """Sum shelf units in store_id (optionally filtered to a single sku_id)."""
    return sum(
        f.units for f in facings
        if f.store_id == store_id and (sku_id is None or f.sku_id == sku_id)
    )


def facings_by_aisle(facings: list[Facing]) -> dict[str, list[Facing]]:
    """Group facings by aisle code."""
    out: dict[str, list[Facing]] = {}
    for f in sorted(facings, key=facing_key):
        out.setdefault(f.loc.aisle, []).append(f)
    return out


def group_facings(facings: list[Facing]) -> dict[str, list[Facing]]:
    """Group facings by store_id."""
    out: dict[str, list[Facing]] = {}
    for f in sorted(facings, key=facing_key):
        out.setdefault(f.store_id, []).append(f)
    return out


def locate_sku(facings: list[Facing], store_id: str, sku_id: str) -> list[Location]:
    """Return all shelf Locations where sku_id is placed in store_id."""
    return [f.loc for f in facings_for_store(facings, store_id) if f.sku_id == sku_id]


def facings_summary(facings: list[Facing]) -> dict:
    """Summarize total facings, stores, SKUs, and shelf units."""
    return {
        "total_facings": len(facings),
        "stores": len({f.store_id for f in facings}),
        "skus": len({f.sku_id for f in facings}),
        "total_units": sum(f.units for f in facings),
    }
