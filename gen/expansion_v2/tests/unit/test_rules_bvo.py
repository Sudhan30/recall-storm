"""Unit tests for recallstorm.rules.bvo."""
from datetime import datetime
from contract import Sku, Verdict
from recallstorm.rules.bvo import (
    bvo_aliases,
    bvo_beverage_scope,
    bvo_effective,
    bvo_evidence,
    bvo_rationale,
    bvo_rules,
    bvo_summary,
    detect_bvo,
    evaluate_bvo_federal,
)


def test_bvo_rules():
    assert "BVO" in bvo_aliases()
    assert bvo_effective() == datetime(2025, 8, 2, 0, 0, 0)
    assert len(bvo_rules()) == 2
    sku = Sku("BV1", "00012345678905", "Citrus Soda", "B", "beverage", "CARBONATED WATER, SUGAR, BVO", True, False, 12, 1.0, 5.0)
    assert bvo_beverage_scope(sku) is True
    m = detect_bvo(sku.ingredients)
    assert m is not None
    assert "21 CFR 180.30" in bvo_rationale(sku, m)
    assert bvo_evidence(sku, m)["rule_id"] == "FDA_BVO_FOOD"
    dec = evaluate_bvo_federal(sku, "NY", datetime(2026, 1, 1))
    assert dec.verdict == Verdict.PULL
    assert bvo_summary([dec])["pulled_count"] == 1
