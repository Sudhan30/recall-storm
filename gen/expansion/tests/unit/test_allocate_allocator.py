"""Unit tests for recallstorm.allocate.allocator."""
from contract import DcStock, Store, StoreFormat
from recallstorm.allocate.allocator import (
    AllocationResult,
    allocate_priority,
    allocate_proportional,
    allocate_substitutes,
    allocation_balance,
    allocation_records,
    never_exceeds_stock,
    round_cases,
    tie_break,
)


def test_allocate_substitutes_and_conservation():
    st1 = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    st2 = Store("WM2", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    stock = [DcStock("DC1", "SUB1", 5)]
    demand = {("WM2", "SUB1"): 4, ("WM1", "SUB1"): 4}

    allocs = allocate_substitutes(demand, stock, [st1, st2])
    assert len(allocs) == 2
    assert allocs[0].store_id == "WM1" and allocs[0].qty_cases == 3 and allocs[0].dc_balance_after == 2
    assert allocs[1].store_id == "WM2" and allocs[1].qty_cases == 2 and allocs[1].dc_balance_after == 0
    assert never_exceeds_stock(stock, allocs) is True
    bal = allocation_balance(stock, allocs)
    assert bal[("DC1", "SUB1")] == 0

    recs = allocation_records(allocs)
    assert recs[0]["type"] == "allocation"
    res = AllocationResult(tuple(allocs), bal)
    assert len(res.allocations) == 2
    assert round_cases(3.9) == 3
    assert tie_break(["WM2", "WM1"]) == ["WM1", "WM2"]
    assert allocate_proportional({"WM1": 2}, 5) == {"WM1": 2}
    assert allocate_priority({"WM1": 2}, 5) == {"WM1": 2}
