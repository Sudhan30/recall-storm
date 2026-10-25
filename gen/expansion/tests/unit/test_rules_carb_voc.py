"""Unit tests for recallstorm.rules.carb_voc."""
from datetime import datetime, timezone
from contract import Sku, Verdict
from recallstorm.rules.carb_voc import (
    carb_voc_rules,
    evaluate_voc,
    lubricant_in_scope,
    parse_voc_percent,
    voc_effective,
    voc_evidence,
    voc_limit_for_category,
    voc_rationale,
    voc_summary,
)


def test_carb_voc_rule():
    assert len(carb_voc_rules()) == 1
    assert voc_effective().year == 2026
    assert voc_limit_for_category("multi-purpose lubricant") == 10.0
    assert parse_voc_percent("PETROLEUM DISTILLATES, VOC: 24.5%") == 24.5

    sku = Sku("LUB1", "00012345678905", "Spray Lubricant", "B", "multi-purpose lubricant", "DISTILLATES, VOC: 25%", False, False, 12, 1.0, 8.0)
    assert lubricant_in_scope(sku) is True
    assert "exceeds" in voc_rationale(sku, 25.0, 10.0)
    dec = evaluate_voc(sku, "CA", datetime(2026, 6, 1, tzinfo=timezone.utc))
    assert dec.verdict == Verdict.PULL
    ev = voc_evidence(sku, 25.0)
    assert ev["rule_id"] == "CARB_LUBRICANT_VOC"
    assert voc_summary([dec])["pulled_count"] == 1
