"""Substitute stock allocation engine implementing allocate_substitutes from contract.py."""
from __future__ import annotations

from dataclasses import dataclass
from contract import Allocation, DcStock, Store
from recallstorm.allocate.stock import conservation_check, stock_after
from recallstorm.core.ids import make_alloc_id
from recallstorm.core.jsonl import record_with_src


@dataclass(frozen=True)
class AllocationResult:
    """Container for substitute allocations and remaining DC stock balances."""

    allocations: tuple[Allocation, ...]
    balances: dict[tuple[str, str], int]


def round_cases(val: float) -> int:
    """Floor a fractional case quantity to a non-negative integer."""
    return max(0, int(val))


def tie_break(store_ids: list[str]) -> list[str]:
    """Deterministically sort store_ids lexicographically."""
    return sorted(store_ids)


def allocate_proportional(demand_for_dc_sku: dict[str, int], available_cases: int) -> dict[str, int]:
    """Allocate available_cases across stores proportionally with deterministic tie-breaking by store_id."""
    if available_cases <= 0 or not demand_for_dc_sku:
        return {}
    clean = {st: int(qty) for st, qty in demand_for_dc_sku.items() if int(qty) > 0}
    if not clean:
        return {}
    total_wanted = sum(clean.values())
    if total_wanted <= available_cases:
        return {st: clean[st] for st in tie_break(list(clean.keys()))}

    # Largest-remainder method with lexicographic store_id tie-break
    exact_shares = {st: (clean[st] * available_cases) / total_wanted for st in clean}
    floors = {st: min(clean[st], int(exact_shares[st])) for st in clean}
    rem_cases = available_cases - sum(floors.values())
    ranked = sorted(
        clean.keys(),
        key=lambda st: (-(exact_shares[st] - floors[st]), -clean[st], st),
    )
    for st in ranked:
        if rem_cases <= 0:
            break
        if floors[st] < clean[st]:
            floors[st] += 1
            rem_cases -= 1
    return {st: floors[st] for st in tie_break(list(floors.keys())) if floors[st] > 0}


def allocate_priority(
    demand_for_dc_sku: dict[str, int],
    available_cases: int,
    stores_by_id: dict[str, Store] | None = None,
) -> dict[str, int]:
    """Allocate cases in deterministic store_id order."""
    return allocate_proportional(demand_for_dc_sku, available_cases)


def allocate_substitutes(
    demand: dict[tuple[str, str], int],
    stock: list[DcStock],
    stores: list[Store],
) -> list[Allocation]:
    """Allocate DC substitute stock to stores without exceeding stock.

    Contract guarantees:
    - Never exceed available DC stock for any (dc_id, sub_sku_id).
    - Integer case quantities > 0.
    - Deterministic tie-breaks by store_id.
    - Exact running dc_balance_after on each emitted Allocation.
    """
    if not isinstance(demand, dict) or not isinstance(stock, list) or not isinstance(stores, list):
        raise TypeError("Expected demand dict, stock list, and stores list")

    stores_by_id = {s.store_id: s for s in stores}
    avail_by_dc_sku: dict[tuple[str, str], int] = {}
    for d in stock:
        if d.cases > 0:
            key = (d.dc_id, d.sku_id)
            avail_by_dc_sku[key] = avail_by_dc_sku.get(key, 0) + int(d.cases)

    # Group demand by (dc_id, sub_sku_id) -> {store_id: cases}
    grouped: dict[tuple[str, str], dict[str, int]] = {}
    for (store_id, sub_sku_id), qty in sorted(demand.items()):
        if qty <= 0 or store_id not in stores_by_id:
            continue
        dc_id = stores_by_id[store_id].dc_id
        grouped.setdefault((dc_id, sub_sku_id), {})[store_id] = (
            grouped.get((dc_id, sub_sku_id), {}).get(store_id, 0) + int(qty)
        )

    allocations: list[Allocation] = []
    for (dc_id, sub_sku_id) in sorted(grouped.keys()):
        avail = avail_by_dc_sku.get((dc_id, sub_sku_id), 0)
        if avail <= 0:
            continue
        store_grants = allocate_proportional(grouped[(dc_id, sub_sku_id)], avail)
        running_bal = avail
        for store_id in tie_break(list(store_grants.keys())):
            granted = store_grants[store_id]
            if granted <= 0:
                continue
            running_bal -= granted
            allocations.append(
                Allocation(
                    alloc_id=make_alloc_id(dc_id, sub_sku_id, store_id),
                    dc_id=dc_id,
                    sub_sku_id=sub_sku_id,
                    store_id=store_id,
                    qty_cases=granted,
                    dc_balance_after=running_bal,
                )
            )
        avail_by_dc_sku[(dc_id, sub_sku_id)] = running_bal

    return allocations


def allocation_balance(stock: list[DcStock], allocations: list[Allocation]) -> dict[tuple[str, str], int]:
    """Return remaining DC stock balances after allocations."""
    return stock_after(stock, allocations)


def never_exceeds_stock(stock: list[DcStock], allocations: list[Allocation]) -> bool:
    """Return True if allocations conserve and never exceed DC stock."""
    return conservation_check(stock, allocations)


def allocation_records(allocations: list[Allocation]) -> list[dict]:
    """Serialize Allocation objects into validated 'allocation' plan.jsonl records."""
    out: list[dict] = []
    for a in allocations:
        payload = {
            "alloc_id": a.alloc_id,
            "dc_id": a.dc_id,
            "sub_sku_id": a.sub_sku_id,
            "store_id": a.store_id,
            "qty_cases": a.qty_cases,
            "dc_balance_after": a.dc_balance_after,
        }
        out.append(record_with_src(payload, "allocation", "recallstorm/allocate/allocator.py"))
    return out
