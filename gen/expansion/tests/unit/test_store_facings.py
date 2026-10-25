"""Unit tests for recallstorm.store.facings."""
from contract import DecidedBy, Facing, Location, SkuDecision, Verdict
from recallstorm.store.facings import (
    affected_facings,
    facing_key,
    facings_by_aisle,
    facings_for_sku,
    facings_for_store,
    facings_summary,
    group_facings,
    locate_sku,
    units_on_shelf,
)


def test_facings_queries():
    f1 = Facing("WM1", "S1", Location("A01", 1, 1, 1), 10)
    f2 = Facing("WM1", "S2", Location("A02", 1, 1, 1), 15)
    facings = [f2, f1]
    assert facing_key(f1)[0] == "WM1"
    assert facings_for_store(facings, "WM1") == [f1, f2]
    assert facings_for_sku(facings, "S1") == [f1]
    decs = {"S1": SkuDecision("S1", Verdict.PULL, "RED3", "Red 3", 0, 5, ("R1",), DecidedBy.RULE, "r")}
    assert affected_facings(facings, decs) == [f1]
    assert units_on_shelf(facings, "WM1") == 25
    assert units_on_shelf(facings, "WM1", "S1") == 10
    assert "A01" in facings_by_aisle(facings)
    assert "WM1" in group_facings(facings)
    assert locate_sku(facings, "WM1", "S1") == [f1.loc]
    assert facings_summary(facings)["total_units"] == 25
