"""Unit tests for recallstorm.plan.explain."""
from contract import DecidedBy, SkuDecision, Verdict
from recallstorm.plan.explain import (
    Explainer,
    explain_allocation,
    explain_route,
    explain_sku,
    explain_store,
    explain_task,
    plan_narrative,
    why_hold,
    why_keep,
)


def test_explain_functions():
    exp = Explainer("ca_red3")
    assert exp.scenario_id == "ca_red3"
    d_hold = SkuDecision("S1", Verdict.HOLD_VERIFY, "RED3", None, None, None, ("R1",), DecidedBy.RULE, "Vague")
    d_keep = SkuDecision("S2", Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, "Clean")
    assert "HOLD_VERIFY" in why_hold(d_hold)
    assert "KEEP" in why_keep(d_keep)
    assert "PULL" in explain_sku({"sku_id": "S1", "verdict": "PULL"}, {"rule_id": "R1", "clause_ref": "c", "rationale": "r"})
    assert "PULL" in explain_task({"task_id": "T1", "action": "PULL", "qty_units": 5, "sku_id": "S1", "store_id": "WM1", "loc": {"aisle": "A01", "bay": 1, "shelf": 1, "pos": 1}, "associate_id": "A1"})
    assert "WM1" in explain_store({"store_id": "WM1", "format": "SUPERCENTER", "deadline": "2027-01-01", "counts": {}})
    assert "ALC-1" in explain_allocation({"alloc_id": "ALC-1", "dc_id": "DC1", "store_id": "WM1", "qty_cases": 2, "sub_sku_id": "SUB1", "dc_balance_after": 1})
    assert "MNF-1" in explain_route({"manifest_id": "MNF-1", "truck_id": "T0", "dc_id": "DC1", "stops": [{}], "depart": "2026-12-31"})
    assert "shelf_task: 1" in plan_narrative([{"type": "shelf_task"}])
