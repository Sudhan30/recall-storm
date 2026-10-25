"""Unit tests for recallstorm.allocate.demand."""
from contract import Allocation, DcStock, DecidedBy, Facing, Location, Sku, SkuDecision, Store, StoreFormat, Verdict
from recallstorm.allocate.demand import (
    DemandTable,
    demand_by_dc,
    demand_by_store,
    demand_cases,
    demand_from_facings,
    demand_to_records,
    substitute_for_sku,
    total_demand,
    unmet_demand,
)


def test_allocate_demand():
    assert demand_cases(25, 12) == 3
    subs = {"S1": ["SUB1", "SUB2"]}
    assert substitute_for_sku("S1", subs, {"SUB2"}) == "SUB2"

    f1 = Facing("WM1", "S1", Location("A01", 1, 1, 1), 20)
    decs = {"S1": SkuDecision("S1", Verdict.PULL, "RED3", "Red 3", 0, 5, ("R1",), DecidedBy.RULE, "")}
    skus = {"SUB1": Sku("SUB1", "00012345678905", "Sub", "B", "c", "I", True, False, 10, 1.0, 5.0)}
    stock = [DcStock("DC1", "SUB1", 5)]
    st = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")

    dem = demand_from_facings([f1], decs, subs, skus, stock)
    assert dem == {("WM1", "SUB1"): 2}
    assert demand_by_store(dem) == {"WM1": 2}
    assert demand_by_dc(dem, [st]) == {("DC1", "SUB1"): 2}
    assert total_demand(dem) == 2
    assert len(demand_to_records(dem)) == 1
    alloc = Allocation("ALC-1", "DC1", "SUB1", "WM1", 1, 4)
    assert unmet_demand(dem, [alloc]) == {("WM1", "SUB1"): 1}
    assert DemandTable(dem).demand == dem
