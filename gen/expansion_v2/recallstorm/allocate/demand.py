"""Calculate substitute SKU case demand from pulled facings."""
from __future__ import annotations

from dataclasses import dataclass, field
import math

from contract import Allocation, DcStock, Facing, Sku, SkuDecision, Store, Verdict


@dataclass
class DemandTable:
    """Table mapping (store_id, sub_sku_id) -> cases demanded."""

    demand: dict[tuple[str, str], int] = field(default_factory=dict)


def demand_cases(units: int, case_units: int) -> int:
    """Convert shelf units to integer cases (ceiling division)."""
    if units <= 0:
        return 0
    cu = max(1, int(case_units))
    return int(math.ceil(units / cu))


def substitute_for_sku(
    sku_id: str,
    substitutes: dict[str, list[str]],
    available_skus: set[str] | None = None,
) -> str | None:
    """Return the first substitute SKU for sku_id (preferring those in available_skus if provided)."""
    candidates = substitutes.get(sku_id) or []
    if not candidates:
        return None
    if available_skus is not None:
        for c in candidates:
            if c in available_skus:
                return c
    return candidates[0]


def demand_from_facings(
    facings: list[Facing],
    decisions: dict[str, SkuDecision],
    substitutes: dict[str, list[str]],
    skus: dict[str, Sku],
    stock: list[DcStock] | None = None,
) -> dict[tuple[str, str], int]:
    """Compute (store_id, sub_sku_id) -> integer cases wanted for all PULL facings."""
    stocked_skus = {d.sku_id for d in stock if d.cases > 0} if stock else None
    units_by_store_sub: dict[tuple[str, str], int] = {}
    for f in facings:
        dec = decisions.get(f.sku_id)
        if not dec or dec.verdict != Verdict.PULL or f.units <= 0:
            continue
        sub_id = substitute_for_sku(f.sku_id, substitutes, available_skus=stocked_skus)
        if not sub_id:
            continue
        key = (f.store_id, sub_id)
        units_by_store_sub[key] = units_by_store_sub.get(key, 0) + f.units

    demand: dict[tuple[str, str], int] = {}
    for (store_id, sub_id), total_units in sorted(units_by_store_sub.items()):
        sub_sku = skus.get(sub_id)
        cu = sub_sku.case_units if sub_sku else 12
        cases = demand_cases(total_units, cu)
        if cases > 0:
            demand[(store_id, sub_id)] = cases
    return demand


def demand_by_store(demand: dict[tuple[str, str], int]) -> dict[str, int]:
    """Sum demanded cases per store_id."""
    out: dict[str, int] = {}
    for (st_id, _), cases in demand.items():
        out[st_id] = out.get(st_id, 0) + cases
    return out


def demand_by_dc(demand: dict[tuple[str, str], int], stores: list[Store]) -> dict[tuple[str, str], int]:
    """Aggregate demanded cases by (dc_id, sub_sku_id)."""
    st_to_dc = {s.store_id: s.dc_id for s in stores}
    out: dict[tuple[str, str], int] = {}
    for (st_id, sub_id), cases in demand.items():
        dc_id = st_to_dc.get(st_id)
        if dc_id:
            key = (dc_id, sub_id)
            out[key] = out.get(key, 0) + cases
    return out


def total_demand(demand: dict[tuple[str, str], int]) -> int:
    """Return total cases demanded across all stores and substitutes."""
    return sum(demand.values())


def unmet_demand(
    demand: dict[tuple[str, str], int], allocations: list[Allocation]
) -> dict[tuple[str, str], int]:
    """Return remaining unmet case demand per (store_id, sub_sku_id)."""
    filled: dict[tuple[str, str], int] = {}
    for a in allocations:
        k = (a.store_id, a.sub_sku_id)
        filled[k] = filled.get(k, 0) + a.qty_cases
    out: dict[tuple[str, str], int] = {}
    for k, want in demand.items():
        rem = max(0, want - filled.get(k, 0))
        if rem > 0:
            out[k] = rem
    return out


def demand_to_records(demand: dict[tuple[str, str], int]) -> list[dict]:
    """Serialize demand dictionary to a list of records."""
    return [
        {"store_id": st_id, "sub_sku_id": sub_id, "want_cases": cases}
        for (st_id, sub_id), cases in sorted(demand.items())
    ]
