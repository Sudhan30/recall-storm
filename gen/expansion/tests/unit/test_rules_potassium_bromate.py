"""Unit tests for recallstorm.rules.potassium_bromate."""
from datetime import datetime, timezone
from contract import Sku, Verdict
from recallstorm.rules.potassium_bromate import (
    bromate_aliases,
    bromate_effective,
    bromate_evidence,
    bromate_rationale,
    bromate_rules,
    bromate_scope,
    bromate_summary,
    detect_bromate,
    evaluate_bromate,
)


def test_potassium_bromate_rule():
    assert "potassium bromate" in bromate_aliases()
    assert len(bromate_rules()) == 1
    assert bromate_effective().year == 2027
    sku = Sku("B1", "00012345678905", "Bread", "Brand", "bakery", "WHEAT FLOUR, POTASSIUM BROMATE, WATER", True, False, 12, 1.0, 5.0)
    assert bromate_scope(sku) is True
    m = detect_bromate(sku.ingredients)
    assert m is not None
    assert "POTASSIUM BROMATE" in bromate_rationale(m)
    dec = evaluate_bromate(sku, datetime(2027, 1, 2, tzinfo=timezone.utc))
    assert dec.verdict == Verdict.PULL
    ev = bromate_evidence(sku, m)
    assert ev["rule_id"] == "CA_AB418_BROMATE"
    assert bromate_summary([dec])["pulled_count"] == 1
