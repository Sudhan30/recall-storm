"""Unit tests for recallstorm.rules.potassium_bromate."""
from datetime import datetime
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


def test_potassium_bromate():
    sku = Sku("B1", "00012345678905", "Bread", "B", "bakery", "WHEAT FLOUR, POTASSIUM BROMATE, WATER", True, False, 12, 1.0, 5.0)
    assert "potassium bromate" in bromate_aliases()
    assert bromate_effective().year == 2027
    assert len(bromate_rules()) == 1
    assert bromate_scope(sku) is True
    m = detect_bromate(sku.ingredients)
    assert m is not None
    assert "CA AB 418" in bromate_rationale(sku, m)
    ev = bromate_evidence(sku, m)
    assert ev["rule_id"] == "CA_AB418_BROMATE"
    dec = evaluate_bromate(sku, "CA", datetime.fromisoformat("2027-01-01T00:00:00-08:00"))
    assert dec.verdict == Verdict.PULL
    assert bromate_summary([dec])["pulled_count"] == 1
