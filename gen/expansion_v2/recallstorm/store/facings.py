"""Query and group store shelf facings."""
from __future__ import annotations

from contract import Facing, Location, SkuDecision, Verdict


def facing_key(facing: Facing) -> tuple[str, str, int, int, int]:
    """Return a deterministic sort key (store_id, aisle, bay, shelf, pos) for a Facing."""
    return (facing.store_id, facing.loc.aisle, facing.loc.bay, facing.loc.shelf, facing.loc.pos)


def facings_for_store(facings: list[Facing], store_id: str) -> list[Facing]:
    """Return facings belonging to store_id sorted by location."""
    return sorted([f for f in facings if f.store_id == store_id], key=facing_key)


def facings_for_sku(facings: list[Facing], sku_id: str) -> list[Facing]:
    """Return facings carrying sku_id sorted by store and location."""
    return sorted([f for f in facings if f.sku_id == sku_id], key=facing_key)


def affected_facings(facings: list[Facing], decisions: dict[str, SkuDecision]) -> list[Facing]:
    """Return facings whose SKU verdict is PULL or HOLD_VERIFY."""
    out = [
        f
        for f in facings
        if f.sku_id in decisions and decisions[f.sku_id].verdict in {Verdict.PULL, Verdict.HOLD_VERIFY}
    ]
    return sorted(out, key=facing_key)


def units_on_shelf(facings: list[Facing], store_id: str | None = None, sku_id: str | None = None) -> int:
    """Sum shelf units across facings, optionally filtered by store_id and/or sku_id."""
    return sum(
        f.units
        for f in facings
        if (store_id is None or f.store_id == store_id) and (sku_id is None or f.sku_id == sku_id)
    )


def facings_by_aisle(facings: list[Facing]) -> dict[str, list[Facing]]:
    """Group facings by aisle code."""
    out: dict[str, list[Facing]] = {}
    for f in sorted(facings, key=facing_key):
        out.setdefault(f.loc.aisle, []).append(f)
    return out


def locate_sku(facings: list[Facing], store_id: str, sku_id: str) -> list[Location]:
    """Return all shelf Locations for sku_id within store_id."""
    return [f.loc for f in facings_for_store(facings, store_id) if f.sku_id == sku_id]


def group_facings(facings: list[Facing]) -> dict[tuple[str, str], list[Facing]]:
    """Group facings by (store_id, sku_id)."""
    out: dict[tuple[str, str], list[Facing]] = {}
    for f in sorted(facings, key=facing_key):
        out.setdefault((f.store_id, f.sku_id), []).append(f)
    return out


def facings_summary(facings: list[Facing]) -> dict:
    """Return summary counts of facings, stores, SKUs, and total units."""
    return {
        "facing_count": len(facings),
        "store_count": len({f.store_id for f in facings}),
        "sku_count": len({f.sku_id for f in facings}),
        "total_units": units_on_shelf(facings),
    }
