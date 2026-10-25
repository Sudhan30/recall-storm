"""Unit tests for recallstorm.rules.carb_voc."""
from datetime import datetime
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


def test_carb_voc():
    assert len(carb_voc_rules()) == 1
    assert voc_effective().year == 2025
    assert voc_limit_for_category("multi-purpose lubricant") == 25.0
    sku = Sku("L1", "00012345678905", "Spray Lubricant", "B", "multi-purpose lubricant", "PETROLEUM DISTILLATES, VOC: 38.5%", False, False, 12, 1.0, 8.0)
    assert lubricant_in_scope(sku) is True
    assert parse_voc_percent(sku.ingredients) == 38.5
    assert "exceeding" in voc_rationale(sku, 38.5, 25.0)
    assert voc_evidence(sku, 38.5)["rule_id"] == "CA_CARB_LUBRICANT_VOC"
    dec = evaluate_voc(sku, "CA", datetime(2026, 1, 1))
    assert dec.verdict == Verdict.PULL
    assert voc_summary([dec])["pulled_count"] == 1
