"""Unit tests for recallstorm.route.returns."""
from contract import DecidedBy, Facing, Location, Sku, SkuDecision, Store, StoreFormat, Verdict
from recallstorm.route.returns import (
    ReturnLoad,
    case_cube,
    case_weight,
    cases_by_dc,
    cases_by_store,
    returned_cases,
    returns_summary,
    returns_to_stops,
    validate_returns,
)


def test_route_returns():
    sku = Sku("S1", "00012345678905", "Sprinkles", "B", "baking", "RED 3", True, False, 6, 2.0, 10.0)
    f = Facing("WM1", "S1", Location("A01", 1, 1, 1), 12)
    decs = {"S1": SkuDecision("S1", Verdict.PULL, "RED3", "RED 3", 0, 5, ("R1",), DecidedBy.RULE, "")}
    st = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")

    assert case_cube(sku, 3) == 6.0
    assert case_weight(sku, 3) == 30.0
    pulled = returned_cases([f], decs, {"S1": sku})
    assert pulled == {("WM1", "S1"): 2}
    assert cases_by_store(pulled) == {"WM1": 2}
    assert cases_by_dc(pulled, [st]) == {"DC1": 2}
    stops = returns_to_stops(pulled, {"S1": sku})
    assert len(stops) == 1 and stops[0].cases == 2 and stops[0].cube_ft3 == 4.0
    assert validate_returns(pulled, {"S1": sku}) == []
    assert returns_summary(pulled, {"S1": sku})["total_cases"] == 2
    assert ReturnLoad("WM1", "S1", 2, 4.0, 20.0).cases == 2
