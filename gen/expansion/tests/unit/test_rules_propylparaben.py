"""Unit tests for recallstorm.rules.propylparaben."""
from datetime import datetime, timezone
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


def test_propylparaben_rule():
    assert "propylparaben" in paraben_aliases()
    assert len(paraben_rules()) == 1
    assert paraben_effective().year == 2027
    sku = Sku("P1", "00012345678905", "Tortilla", "Brand", "bakery", "CORN, WATER, PROPYLPARABEN", True, False, 12, 1.0, 5.0)
    assert paraben_scope(sku) is True
    m = detect_propylparaben(sku.ingredients)
    assert m is not None
    assert "PROPYLPARABEN" in paraben_rationale(m)
    dec = evaluate_propylparaben(sku, datetime(2027, 1, 2, tzinfo=timezone.utc))
    assert dec.verdict == Verdict.PULL
    ev = paraben_evidence(sku, m)
    assert ev["rule_id"] == "CA_AB418_PROPYLPARABEN"
    assert paraben_summary([dec])["pulled_count"] == 1
