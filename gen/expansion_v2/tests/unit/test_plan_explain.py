"""Unit tests for recallstorm.plan.explain."""
from datetime import datetime
from contract import Allocation, DecidedBy, RouteManifest, SkuDecision, Stop, Verdict
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


def test_plan_explain():
    assert "TSK-1" in explain_task({"task_id": "TSK-1", "action": "PULL", "qty_units": 5, "sku_id": "S1", "store_id": "WM1", "associate_id": "A1", "window": []})
    assert "WM1" in explain_store({"store_id": "WM1", "format": "SUPERCENTER", "counts": {}, "deadline": "2027-01-01"})
    assert "PULL" in explain_sku({"sku_id": "S1", "verdict": "PULL", "rule_ids": ["R1"]}, {"evidence_id": "EVD-1", "rationale": "Red 3"})
    alloc = Allocation("ALC-1", "DC1", "SUB1", "WM1", 2, 3)
    assert "ALC-1" in explain_allocation(alloc)
    mnf = RouteManifest("MNF-1", "T1", "DC1", (Stop("WM1", 2, 3.0, 10.0),), datetime(2026, 12, 31, 8, 0))
    assert "MNF-1" in explain_route(mnf)
    d_hold = SkuDecision("S1", Verdict.HOLD_VERIFY, "RED3", None, None, None, ("R1",), DecidedBy.RULE, "Unclear")
    d_keep = SkuDecision("S2", Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, "Clean")
    assert "Unclear" in why_hold(d_hold)
    assert "Clean" in why_keep(d_keep)
    nar = plan_narrative([{"type": "run"}, {"type": "shelf_task"}])
    assert "run=1" in nar
    assert Explainer([{"type": "run"}]).summary_text() == "Plan Summary: run=1"
