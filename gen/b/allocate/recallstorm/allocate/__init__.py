"""Substitute stock allocation across stores within each distribution center."""
from __future__ import annotations

from collections import defaultdict
from contract import Allocation, DcStock, Store

SRC_PATH = "recallstorm/allocate/__init__.py"


def allocate_substitutes(
    demand: dict[tuple[str, str], int],
    stock: list[DcStock],
    stores: list[Store],
) -> list[Allocation]:
    """Allocate DC substitute stock to stores fairly and deterministically.

    Each store draws only from its assigned DC (Store.dc_id).
    Never exceeds DcStock.cases; allocates integer cases only.
    When stock is short at a DC for a given substitute SKU, splits available
    cases proportionally using the largest-remainder method and breaks ties
    deterministically by store_id ascending.
    """
    store_by_id: dict[str, Store] = {}
    known_dcs: set[str] = set()
    for store in stores:
        if not store.store_id or not isinstance(store.store_id, str):
            raise ValueError(f"Invalid store_id in stores: {store!r}")
        if not store.dc_id or not isinstance(store.dc_id, str):
            raise ValueError(f"Unknown or empty dc_id for store {store.store_id!r}")
        if store.store_id in store_by_id:
            raise ValueError(f"Duplicate store_id in stores: {store.store_id!r}")
        store_by_id[store.store_id] = store
        known_dcs.add(store.dc_id)

    dc_inventory: dict[tuple[str, str], int] = defaultdict(int)
    for item in stock:
        if not item.dc_id or item.dc_id not in known_dcs:
            raise ValueError(f"Unknown DC in stock: {item.dc_id!r}")
        if not item.sku_id or not isinstance(item.sku_id, str):
            raise ValueError(f"Invalid sku_id in stock: {item!r}")
        if not isinstance(item.cases, int) or isinstance(item.cases, bool) or item.cases < 0:
            raise ValueError(
                f"Negative or non-integer stock cases for ({item.dc_id!r}, {item.sku_id!r}): {item.cases!r}"
            )
        dc_inventory[(item.dc_id, item.sku_id)] += item.cases

    grouped_demand: dict[tuple[str, str], dict[str, int]] = defaultdict(dict)
    for key, cases_wanted in demand.items():
        if not isinstance(key, tuple) or len(key) != 2:
            raise ValueError(f"Invalid demand key (expected (store_id, sub_sku_id)): {key!r}")
        store_id, sub_sku_id = key
        if store_id not in store_by_id:
            raise ValueError(f"Unknown store in demand: {store_id!r}")
        if not sub_sku_id or not isinstance(sub_sku_id, str):
            raise ValueError(f"Invalid sub_sku_id in demand: {sub_sku_id!r}")
        if not isinstance(cases_wanted, int) or isinstance(cases_wanted, bool) or cases_wanted < 0:
            raise ValueError(
                f"Negative or non-integer demand for ({store_id!r}, {sub_sku_id!r}): {cases_wanted!r}"
            )
        if cases_wanted > 0:
            dc_id = store_by_id[store_id].dc_id
            grouped_demand[(dc_id, sub_sku_id)][store_id] = cases_wanted

    allocations: list[Allocation] = []

    for dc_id, sub_sku_id in sorted(grouped_demand.keys()):
        store_demands = grouped_demand[(dc_id, sub_sku_id)]
        available = dc_inventory.get((dc_id, sub_sku_id), 0)
        if available <= 0:
            continue

        total_wanted = sum(store_demands.values())
        sorted_stores = sorted(store_demands.keys())

        if available >= total_wanted:
            granted_by_store = {sid: store_demands[sid] for sid in sorted_stores}
        else:
            granted_by_store = {}
            remainders: list[tuple[int, int, str]] = []
            allocated_sum = 0
            for sid in sorted_stores:
                wanted = store_demands[sid]
                numerator = available * wanted
                base_cases = numerator // total_wanted
                rem = numerator % total_wanted
                granted_by_store[sid] = base_cases
                allocated_sum += base_cases
                remainders.append((-rem, -wanted, sid))

            leftover = available - allocated_sum
            remainders.sort(key=lambda item: (item[0], item[1], item[2]))
            for i in range(leftover):
                sid = remainders[i][2]
                granted_by_store[sid] += 1

        running_balance = available
        for sid in sorted_stores:
            qty = granted_by_store[sid]
            if qty > 0:
                running_balance -= qty
                alloc_id = f"ALLOC-{dc_id}-{sub_sku_id}-{sid}"
                allocations.append(
                    Allocation(
                        alloc_id=alloc_id,
                        dc_id=dc_id,
                        sub_sku_id=sub_sku_id,
                        store_id=sid,
                        qty_cases=qty,
                        dc_balance_after=running_balance,
                    )
                )

    return allocations


__all__ = ["SRC_PATH", "allocate_substitutes"]
