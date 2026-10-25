"""Unit tests for recallstorm.allocate."""
from __future__ import annotations

from contract import DcStock, Store, StoreFormat
from recallstorm.allocate import allocate_substitutes


def _sample_stores() -> list[Store]:
    return [
        Store("CA1000", StoreFormat.SUPERCENTER, "CA", "Sacramento", 38.5, -121.5, "D01", "DC_NORTH", "America/Los_Angeles"),
        Store("CA1007", StoreFormat.SUPERCENTER, "CA", "Stockton", 37.9, -121.3, "D01", "DC_NORTH", "America/Los_Angeles"),
        Store("CA1001", StoreFormat.SUPERCENTER, "CA", "Fresno", 36.7, -119.7, "D01", "DC_CENTRAL", "America/Los_Angeles"),
    ]


def test_allocate_never_exceeds_stock_and_breaks_ties_by_store_id() -> None:
    stores = _sample_stores()
    stock = [
        DcStock(dc_id="DC_NORTH", sku_id="SUB1", cases=5),
        DcStock(dc_id="DC_CENTRAL", sku_id="SUB1", cases=2),
    ]
    demand = {
        ("CA1007", "SUB1"): 4,
        ("CA1000", "SUB1"): 3,
        ("CA1001", "SUB1"): 5,
    }
    allocs = allocate_substitutes(demand, stock, stores)
    # CA1000 goes before CA1007 in DC_NORTH
    assert len(allocs) == 3
    by_store = {a.store_id: a for a in allocs}

    assert by_store["CA1000"].qty_cases == 3
    assert by_store["CA1000"].dc_balance_after == 2

    assert by_store["CA1007"].qty_cases == 2
    assert by_store["CA1007"].dc_balance_after == 0

    assert by_store["CA1001"].qty_cases == 2
    assert by_store["CA1001"].dc_balance_after == 0


def test_allocate_zero_or_missing_stock_skipped() -> None:
    stores = _sample_stores()
    stock = [DcStock(dc_id="DC_NORTH", sku_id="SUB1", cases=0)]
    demand = {("CA1000", "SUB1"): 2, ("CA1000", "SUB2"): 2}
    allocs = allocate_substitutes(demand, stock, stores)
    assert allocs == []
