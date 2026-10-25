"""Unit tests for recallstorm.rules.propylparaben."""
from datetime import datetime
from contract import Sku, Verdict
from recallstorm.rules.propylparaben import (
    detect_propylparaben,
    evaluate_propylparaben,
    paraben_aliases,
    paraben_effective,
    paraben_evidence,
    paraben_rationale,
    paraben_rules,
    paraben_scope,
    paraben_summary,
)


def test_propylparaben():
    sku = Sku("P1", "00012345678905", "Tortilla", "B", "bakery", "CORN, PROPYLPARABEN, WATER", True, False, 12, 1.0, 5.0)
    assert "propylparaben" in paraben_aliases()
    assert paraben_effective().year == 2027
    assert len(paraben_rules()) == 1
    assert paraben_scope(sku) is True
    m = detect_propylparaben(sku.ingredients)
    assert m is not None
    assert "CA AB 418" in paraben_rationale(sku, m)
    assert paraben_evidence(sku, m)["rule_id"] == "CA_AB418_PROPYLPARABEN"
    dec = evaluate_propylparaben(sku, "CA", datetime(2027, 1, 1))
    assert dec.verdict == Verdict.PULL
    assert paraben_summary([dec])["pulled_count"] == 1
