"""Compute store-level substitute case demand from pulled shelf facings."""
from __future__ import annotations

import math
from dataclasses import dataclass
from contract import Allocation, DcStock, Facing, Sku, SkuDecision, Store, Verdict


@dataclass(frozen=True)
class DemandTable:
    """Wrapper around (store_id, sub_sku_id) -> cases demand dictionary."""

    entries: dict[tuple[str, str], int]


def demand_cases(units: int, case_units: int = 12) -> int:
    """Convert shelf unit count to whole cases (minimum 1 case when units > 0)."""
    if units <= 0:
        return 0
    cu = max(1, case_units)
    return max(1, math.ceil(units / cu))


def substitute_for_sku(
    sku_id: str,
    substitutes: dict[str, list[str]],
    dc_id: str | None = None,
    stock_map: dict[tuple[str, str], int] | None = None,
) -> str | None:
    """Pick the best approved substitute SKU for a pulled sku_id, preferring one in stock at dc_id."""
    cands = substitutes.get(sku_id, [])
    if not cands:
        return None
    if dc_id and stock_map:
        for sub_id in cands:
            if stock_map.get((dc_id, sub_id), 0) > 0:
                return sub_id
    return cands[0]


def demand_from_facings(
    facings: list[Facing],
    decisions: dict[str, SkuDecision],
    substitutes: dict[str, list[str]],
    skus_by_id: dict[str, Sku],
    dc_stock: list[DcStock] | None = None,
    stores_by_id: dict[str, Store] | None = None,
) -> dict[tuple[str, str], int]:
    """Compute (store_id, sub_sku_id) -> cases wanted for all PULL facings."""
    stock_map: dict[tuple[str, str], int] = {}
    for d in dc_stock or []:
        stock_map[(d.dc_id, d.sku_id)] = stock_map.get((d.dc_id, d.sku_id), 0) + d.cases

    units_by_store_sub: dict[tuple[str, str], int] = {}
    for f in facings:
        dec = decisions.get(f.sku_id)
        if dec is None or dec.verdict != Verdict.PULL:
            continue
        dc_id = stores_by_id[f.store_id].dc_id if (stores_by_id and f.store_id in stores_by_id) else None
        sub_id = substitute_for_sku(f.sku_id, substitutes, dc_id, stock_map)
        if not sub_id:
            continue
        key = (f.store_id, sub_id)
        units_by_store_sub[key] = units_by_store_sub.get(key, 0) + f.units

    demand: dict[tuple[str, str], int] = {}
    for (st_id, sub_id), units in sorted(units_by_store_sub.items()):
        sub_sku = skus_by_id.get(sub_id)
        cu = sub_sku.case_units if sub_sku else 12
        demand[(st_id, sub_id)] = demand_cases(units, cu)
    return demand


def demand_by_dc(demand: dict[tuple[str, str], int], stores_by_id: dict[str, Store]) -> dict[tuple[str, str], int]:
    """Aggregate demand into (dc_id, sub_sku_id) -> total cases wanted."""
    out: dict[tuple[str, str], int] = {}
    for (st_id, sub_id), cases in demand.items():
        if st_id in stores_by_id and cases > 0:
            dc_id = stores_by_id[st_id].dc_id
            out[(dc_id, sub_id)] = out.get((dc_id, sub_id), 0) + cases
    return out


def demand_by_store(demand: dict[tuple[str, str], int]) -> dict[str, int]:
    """Aggregate total substitute cases wanted per store_id."""
    out: dict[str, int] = {}
    for (st_id, _), cases in demand.items():
        out[st_id] = out.get(st_id, 0) + cases
    return out


def total_demand(demand: dict[tuple[str, str], int]) -> int:
    """Return total cases demanded across all stores and substitutes."""
    return sum(v for v in demand.values() if v > 0)


def unmet_demand(demand: dict[tuple[str, str], int], allocations: list[Allocation]) -> dict[tuple[str, str], int]:
    """Compute remaining unfulfilled case demand after allocations."""
    filled: dict[tuple[str, str], int] = {}
    for a in allocations:
        key = (a.store_id, a.sub_sku_id)
        filled[key] = filled.get(key, 0) + a.qty_cases
    out: dict[tuple[str, str], int] = {}
    for key, wanted in demand.items():
        short = max(0, wanted - filled.get(key, 0))
        if short > 0:
            out[key] = short
    return out


def demand_to_records(demand: dict[tuple[str, str], int]) -> list[dict]:
    """Serialize demand dictionary to a sorted list of records."""
    return [
        {"store_id": st, "sub_sku_id": sub, "cases": cases}
        for (st, sub), cases in sorted(demand.items())
    ]
