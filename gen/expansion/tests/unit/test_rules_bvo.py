"""Unit tests for recallstorm.rules.bvo."""
from datetime import datetime, timezone
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


def test_bvo_evaluation():
    assert "BVO" in bvo_aliases()
    assert len(bvo_rules()) == 2
    assert bvo_effective("US") < bvo_effective("CA")
    sku = Sku("BV1", "00012345678905", "Citrus Soda", "B", "soda", "CARBONATED WATER, SUGAR, BVO", True, False, 12, 1.0, 5.0)
    assert bvo_beverage_scope(sku) is True
    m = detect_bvo(sku.ingredients)
    assert m is not None
    assert "BVO" in bvo_rationale(m)
    dec = evaluate_bvo_federal(sku, datetime(2026, 12, 30, tzinfo=timezone.utc))
    assert dec.verdict == Verdict.PULL
    ev = bvo_evidence(sku, m)
    assert ev["rule_id"] == "FDA_BVO_FOOD"
    assert bvo_summary([dec])["pulled_count"] == 1
