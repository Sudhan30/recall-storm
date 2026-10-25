"""Deterministic DC substitute inventory allocation."""
from __future__ import annotations

from contract import Allocation, DcStock, Store


def allocate_substitutes(
    demand: dict[tuple[str, str], int],
    stock: list[DcStock],
    stores: list[Store],
) -> list[Allocation]:
    """Allocate substitute cases from each store's DC without exceeding DC stock.

    Deterministic ordering and tie-breaking by (store_id, sub_sku_id).
    """
    store_to_dc: dict[str, str] = {s.store_id: s.dc_id for s in stores}

    # Aggregate available stock by (dc_id, sku_id)
    available: dict[tuple[str, str], int] = {}
    for item in stock:
        if item.cases > 0:
            key = (item.dc_id, item.sku_id)
            available[key] = available.get(key, 0) + int(item.cases)

    allocations: list[Allocation] = []
    seq = 0

    for (store_id, sub_sku_id), wanted in sorted(demand.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        wanted_cases = int(wanted)
        if wanted_cases <= 0:
            continue
        dc_id = store_to_dc.get(store_id)
        if dc_id is None:
            continue

        stock_key = (dc_id, sub_sku_id)
        avail = available.get(stock_key, 0)
        if avail <= 0:
            continue

        granted = min(wanted_cases, avail)
        if granted <= 0:
            continue

        balance_after = avail - granted
        available[stock_key] = balance_after
        alloc_id = f"ALLOC-{seq:05d}"
        seq += 1
        allocations.append(
            Allocation(
                alloc_id=alloc_id,
                dc_id=dc_id,
                sub_sku_id=sub_sku_id,
                store_id=store_id,
                qty_cases=granted,
                dc_balance_after=balance_after,
            )
        )

    return allocations
