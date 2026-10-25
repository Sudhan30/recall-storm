"""Unit tests for recallstorm.allocate.allocate_substitutes."""
from __future__ import annotations

import pytest
from contract import Allocation, DcStock, Store, StoreFormat
from recallstorm.allocate import allocate_substitutes


def _make_store(store_id: str, dc_id: str = "DC_NORTH") -> Store:
    return Store(
        store_id=store_id,
        format=StoreFormat.SUPERCENTER,
        state="CA",
        city="Sacramento",
        lat=38.58,
        lon=-121.49,
        district="D01",
        dc_id=dc_id,
        tz="America/Los_Angeles",
    )


def test_full_satisfaction_and_running_dc_balance() -> None:
    stores = [_make_store("WM1002", "DC_NORTH"), _make_store("WM1001", "DC_NORTH")]
    stock = [DcStock(dc_id="DC_NORTH", sku_id="SUB_A", cases=10)]
    demand = {
        ("WM1002", "SUB_A"): 4,
        ("WM1001", "SUB_A"): 3,
    }

    result = allocate_substitutes(demand, stock, stores)

    assert result == [
        Allocation(
            alloc_id="ALLOC-DC_NORTH-SUB_A-WM1001",
            dc_id="DC_NORTH",
            sub_sku_id="SUB_A",
            store_id="WM1001",
            qty_cases=3,
            dc_balance_after=7,
        ),
        Allocation(
            alloc_id="ALLOC-DC_NORTH-SUB_A-WM1002",
            dc_id="DC_NORTH",
            sub_sku_id="SUB_A",
            store_id="WM1002",
            qty_cases=4,
            dc_balance_after=3,
        ),
    ]


def test_short_stock_equal_demand_tie_break_by_store_id() -> None:
    stores = [
        _make_store("WM300", "DC_CENTRAL"),
        _make_store("WM100", "DC_CENTRAL"),
        _make_store("WM200", "DC_CENTRAL"),
    ]
    stock = [DcStock(dc_id="DC_CENTRAL", sku_id="SUB_B", cases=5)]
    demand = {
        ("WM300", "SUB_B"): 3,
        ("WM100", "SUB_B"): 3,
        ("WM200", "SUB_B"): 3,
    }

    result = allocate_substitutes(demand, stock, stores)

    assert [(a.store_id, a.qty_cases, a.dc_balance_after) for a in result] == [
        ("WM100", 2, 3),
        ("WM200", 2, 1),
        ("WM300", 1, 0),
    ]


def test_short_stock_proportional_split_and_zero_filtered() -> None:
    stores = [
        _make_store("WM01", "DC_SOUTH"),
        _make_store("WM02", "DC_SOUTH"),
        _make_store("WM03", "DC_SOUTH"),
    ]
    stock = [DcStock(dc_id="DC_SOUTH", sku_id="SUB_C", cases=2)]
    demand = {
        ("WM01", "SUB_C"): 1,
        ("WM02", "SUB_C"): 4,
        ("WM03", "SUB_C"): 5,
    }

    result = allocate_substitutes(demand, stock, stores)

    # Quotas: WM01 = 0.2, WM02 = 0.8, WM03 = 1.0 -> WM03 gets 1, WM02 gets 1, WM01 gets 0 (omitted)
    assert [(a.store_id, a.qty_cases, a.dc_balance_after) for a in result] == [
        ("WM02", 1, 1),
        ("WM03", 1, 0),
    ]


def test_store_draws_only_from_own_dc() -> None:
    stores = [
        _make_store("WM_NORTH", "DC_NORTH"),
        _make_store("WM_SOUTH", "DC_SOUTH"),
    ]
    stock = [DcStock(dc_id="DC_NORTH", sku_id="SUB_X", cases=20)]
    demand = {
        ("WM_SOUTH", "SUB_X"): 5,
        ("WM_NORTH", "SUB_X"): 0,
    }

    result = allocate_substitutes(demand, stock, stores)
    assert result == []


def test_validation_rejects_negative_demand_unknown_store_and_unknown_dc() -> None:
    stores = [_make_store("WM100", "DC_NORTH")]
    stock = [DcStock(dc_id="DC_NORTH", sku_id="SUB_A", cases=5)]

    with pytest.raises(ValueError, match="Negative"):
        allocate_substitutes({("WM100", "SUB_A"): -1}, stock, stores)

    with pytest.raises(ValueError, match="Unknown store"):
        allocate_substitutes({("WM999", "SUB_A"): 2}, stock, stores)

    with pytest.raises(ValueError, match="Unknown DC"):
        bad_stock = [DcStock(dc_id="DC_UNKNOWN", sku_id="SUB_A", cases=5)]
        allocate_substitutes({("WM100", "SUB_A"): 2}, bad_stock, stores)

    with pytest.raises(ValueError, match="Negative"):
        neg_stock = [DcStock(dc_id="DC_NORTH", sku_id="SUB_A", cases=-3)]
        allocate_substitutes({("WM100", "SUB_A"): 2}, neg_stock, stores)
