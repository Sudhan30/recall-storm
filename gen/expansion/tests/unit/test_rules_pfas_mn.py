"""Unit tests for recallstorm.rules.pfas_mn."""
from datetime import datetime, timezone
from contract import Sku, Verdict
from recallstorm.rules.pfas_mn import (
    detect_pfas_claim,
    evaluate_pfas,
    pfas_effective,
    pfas_evidence,
    pfas_in_scope,
    pfas_product_categories,
    pfas_rationale,
    pfas_rules,
    pfas_summary,
)


def test_pfas_mn_rule():
    assert len(pfas_product_categories()) == 11
    assert len(pfas_rules()) == 1
    assert pfas_effective().year == 2025
    sku = Sku("PF1", "00012345678905", "Nonstick Fry Pan", "B", "cookware", "ALUMINUM, PTFE COATING", False, False, 6, 2.0, 12.0)
    assert pfas_in_scope(sku) is True
    m = detect_pfas_claim(sku.ingredients)
    assert m is not None
    assert "PTFE" in pfas_rationale(sku, m)
    dec = evaluate_pfas(sku, "MN", datetime(2026, 1, 1, tzinfo=timezone.utc))
    assert dec.verdict == Verdict.PULL
    assert evaluate_pfas(sku, "CA", datetime(2026, 1, 1, tzinfo=timezone.utc)).verdict == Verdict.KEEP
    ev = pfas_evidence(sku, m)
    assert ev["rule_id"] == "MN_PFAS_116_943"
    assert pfas_summary([dec])["pulled_count"] == 1
