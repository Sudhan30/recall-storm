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


def test_demand_calculations():
    assert demand_cases(15, 12) == 2
    assert demand_cases(0, 12) == 0
    subs = {"S1": ["SUB1", "SUB2"]}
    assert substitute_for_sku("S1", subs, "DC1", {("DC1", "SUB2"): 5}) == "SUB2"

    f = Facing("WM1", "S1", Location("A01", 1, 1, 1), 15)
    decs = {"S1": SkuDecision("S1", Verdict.PULL, "RED3", "Red 3", 0, 5, ("R1",), DecidedBy.RULE, "r")}
    skus = {"SUB2": Sku("SUB2", "00012345678905", "Sub", "B", "c", "SUGAR", True, False, 12, 1.0, 5.0)}
    st = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    stock = [DcStock("DC1", "SUB2", 5)]

    dem = demand_from_facings([f], decs, subs, skus, stock, {"WM1": st})
    dt = DemandTable(dem)
    assert dt.entries == {("WM1", "SUB2"): 2}
    assert demand_by_dc(dem, {"WM1": st}) == {("DC1", "SUB2"): 2}
    assert demand_by_store(dem) == {"WM1": 2}
    assert total_demand(dem) == 2
    assert len(demand_to_records(dem)) == 1
    alloc = Allocation("ALC-1", "DC1", "SUB2", "WM1", 1, 4)
    assert unmet_demand(dem, [alloc]) == {("WM1", "SUB2"): 1}
