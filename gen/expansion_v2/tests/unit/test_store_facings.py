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


def test_store_facings():
    f1 = Facing("WM1", "S1", Location("A01", 1, 1, 1), 10)
    f2 = Facing("WM1", "S2", Location("A02", 1, 1, 1), 15)
    decs = {
        "S1": SkuDecision("S1", Verdict.PULL, "RED3", "Red 3", 0, 5, ("R1",), DecidedBy.RULE, ""),
        "S2": SkuDecision("S2", Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, ""),
    }
    assert facing_key(f1)[0] == "WM1"
    assert len(facings_for_store([f1, f2], "WM1")) == 2
    assert len(facings_for_sku([f1, f2], "S1")) == 1
    assert affected_facings([f1, f2], decs) == [f1]
    assert units_on_shelf([f1, f2], "WM1") == 25
    assert "A01" in facings_by_aisle([f1, f2])
    assert len(locate_sku([f1, f2], "WM1", "S1")) == 1
    assert len(group_facings([f1, f2])) == 2
    assert facings_summary([f1, f2])["total_units"] == 25
