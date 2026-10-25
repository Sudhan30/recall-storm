"""Substitute allocation engine implementing allocate_substitutes from contract.py."""
from __future__ import annotations

from dataclasses import dataclass, field
import math

from contract import Allocation, DcStock, Store
from recallstorm.allocate.stock import conservation_check, stock_ledger
from recallstorm.core.ids import make_alloc_id


@dataclass
class AllocationResult:
    """Container for Allocation records and DC balances."""

    allocations: list[Allocation] = field(default_factory=list)


def round_cases(val: float) -> int:
    """Floor a floating-point case count to a non-negative integer."""
    return max(0, int(math.floor(float(val))))


def tie_break(store_ids: list[str]) -> list[str]:
    """Deterministically order store_ids lexicographically."""
    return sorted(store_ids)


def allocate_proportional(want_by_store: dict[str, int], available_cases: int) -> dict[str, int]:
    """Allocate available_cases across stores proportionally with deterministic largest-remainder tie-breaks by store_id."""
    positive = {st: int(w) for st, w in want_by_store.items() if int(w) > 0}
    if not positive or available_cases <= 0:
        return {}
    total_want = sum(positive.values())
    if available_cases >= total_want:
        return {st: positive[st] for st in tie_break(list(positive.keys()))}

    # Proportional quota with largest remainder, tie-breaking by store_id ascending
    quotas: dict[str, float] = {st: (positive[st] * available_cases) / total_want for st in positive}
    granted: dict[str, int] = {st: int(math.floor(quotas[st])) for st in positive}
    rem = available_cases - sum(granted.values())
    if rem > 0:
        ranked = sorted(
            positive.keys(),
            key=lambda st: (-(quotas[st] - granted[st]), -positive[st], st),
        )
        for st in ranked[:rem]:
            granted[st] += 1
    return {st: granted[st] for st in tie_break(list(granted.keys())) if granted[st] > 0}


def allocate_priority(
    want_by_store: dict[str, int], available_cases: int, stores: dict[str, Store]
) -> dict[str, int]:
    """Allocate available_cases to stores ordered by store_id."""
    return allocate_proportional(want_by_store, available_cases)


def allocate_substitutes(
    demand: dict[tuple[str, str], int],
    stock: list[DcStock],
    stores: list[Store],
) -> list[Allocation]:
    """Allocate DC substitute stock to stores.

    Implements the contract.py signature and invariants:
      - Never exceed DC stock for any (dc_id, sub_sku_id)
      - Integer cases only (qty_cases > 0)
      - Deterministic tie-breaks by store_id
      - Accurate running dc_balance_after on every Allocation
    """
    if not demand or not stock or not stores:
        return []

    store_to_dc = {s.store_id: s.dc_id for s in stores}
    ledger = stock_ledger(stock)

    # Group demand by (dc_id, sub_sku_id) -> {store_id: cases_wanted}
    by_dc_sub: dict[tuple[str, str], dict[str, int]] = {}
    for (store_id, sub_sku_id), want in demand.items():
        if int(want) <= 0 or store_id not in store_to_dc:
            continue
        dc_id = store_to_dc[store_id]
        bucket = by_dc_sub.setdefault((dc_id, sub_sku_id), {})
        bucket[store_id] = bucket.get(store_id, 0) + int(want)

    out: list[Allocation] = []
    for (dc_id, sub_sku_id) in sorted(by_dc_sub.keys()):
        avail = ledger.available.get((dc_id, sub_sku_id), 0)
        if avail <= 0:
            continue
        want_map = by_dc_sub[(dc_id, sub_sku_id)]
        granted_map = allocate_proportional(want_map, avail)
        running_bal = avail
        for store_id in tie_break(list(granted_map.keys())):
            qty = granted_map[store_id]
            if qty <= 0:
                continue
            running_bal -= qty
            ledger.available[(dc_id, sub_sku_id)] = running_bal
            out.append(
                Allocation(
                    alloc_id=make_alloc_id(dc_id, store_id, sub_sku_id),
                    dc_id=dc_id,
                    sub_sku_id=sub_sku_id,
                    store_id=store_id,
                    qty_cases=qty,
                    dc_balance_after=running_bal,
                )
            )
    return out


def allocation_balance(stock: list[DcStock], allocations: list[Allocation]) -> dict[tuple[str, str], int]:
    """Return final remaining cases per (dc_id, sub_sku_id) after allocations."""
    ledger = stock_ledger(stock)
    for a in allocations:
        key = (a.dc_id, a.sub_sku_id)
        ledger.available[key] = ledger.available.get(key, 0) - a.qty_cases
    return dict(ledger.available)


def never_exceeds_stock(stock: list[DcStock], allocations: list[Allocation]) -> bool:
    """Return True if allocations conserve and never exceed DC stock."""
    return conservation_check(stock, allocations)


def allocation_records(allocations: list[Allocation]) -> list[dict]:
    """Convert Allocation objects into plan.jsonl 'allocation' records."""
    return [
        {
            "type": "allocation",
            "alloc_id": a.alloc_id,
            "dc_id": a.dc_id,
            "sub_sku_id": a.sub_sku_id,
            "store_id": a.store_id,
            "qty_cases": a.qty_cases,
            "dc_balance_after": a.dc_balance_after,
            "src": "recallstorm/allocate/allocator.py",
        }
        for a in allocations
    ]
