"""Unit tests for recallstorm.route.returns."""
from datetime import datetime, timezone
from contract import DecidedBy, Facing, Location, RouteManifest, Sku, SkuDecision, Store, StoreFormat, Verdict
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


def test_returns_calculations():
    sku = Sku("S1", "00012345678905", "Candy", "B", "candy", "RED 3", True, False, 12, 2.0, 10.0)
    assert case_cube(sku, 3) == 6.0
    assert case_weight(sku, 3) == 30.0

    f = Facing("WM1", "S1", Location("A01", 1, 1, 1), 25)
    decs = {"S1": SkuDecision("S1", Verdict.PULL, "RED3", "Red 3", 0, 5, ("R1",), DecidedBy.RULE, "r")}
    pulled = returned_cases([f], decs, {"S1": sku})
    assert pulled == {("WM1", "S1"): 3}
    assert cases_by_store(pulled) == {"WM1": 3}

    st = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    assert cases_by_dc(pulled, {"WM1": st}) == {"DC1": 3}
    stops = returns_to_stops(pulled, {"S1": sku})
    assert len(stops) == 1 and stops[0].cases == 3
    mnf = RouteManifest("MNF-1", "T0", "DC1", tuple(stops), datetime(2026, 12, 31, 8, 0, tzinfo=timezone.utc))
    assert validate_returns(pulled, [mnf]) == []
    assert returns_summary(pulled, {"S1": sku})["total_cases"] == 3
    rl = ReturnLoad("WM1", "S1", 3, 6.0, 30.0)
    assert rl.cases == 3
