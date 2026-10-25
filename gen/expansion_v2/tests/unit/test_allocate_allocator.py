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
from recallstorm.core.jsonl import validate_record


def test_allocate_substitutes_basic():
    s1 = Store("WM1001", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC_NORTH", "America/Los_Angeles")
    s2 = Store("WM1002", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC_NORTH", "America/Los_Angeles")
    stock = [DcStock("DC_NORTH", "VAR0172", 5)]
    demand = {("WM1001", "VAR0172"): 4, ("WM1002", "VAR0172"): 4}

    allocs = allocate_substitutes(demand, stock, [s1, s2])
    assert len(allocs) == 2
    assert sum(a.qty_cases for a in allocs) == 5
    # Tie-break by store_id gives WM1001 3 cases and WM1002 2 cases
    assert allocs[0].store_id == "WM1001" and allocs[0].qty_cases == 3 and allocs[0].dc_balance_after == 2
    assert allocs[1].store_id == "WM1002" and allocs[1].qty_cases == 2 and allocs[1].dc_balance_after == 0
    assert never_exceeds_stock(stock, allocs) is True
    assert allocation_balance(stock, allocs)[("DC_NORTH", "VAR0172")] == 0

    recs = allocation_records(allocs)
    assert validate_record(recs[0], "allocation") == []
    assert round_cases(3.9) == 3
    assert tie_break(["B", "A"]) == ["A", "B"]
    assert allocate_priority({"WM1": 2}, 5, {"WM1": s1}) == {"WM1": 2}
    assert allocate_proportional({"WM1": 2}, 5) == {"WM1": 2}
    assert len(AllocationResult(allocs).allocations) == 2
