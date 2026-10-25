"""Edge case tests for recallstorm.rules.carb_voc."""
from datetime import datetime
from contract import Sku, Verdict
from recallstorm.rules.carb_voc import evaluate_voc, parse_voc_percent


def test_carb_voc_edge():
    assert parse_voc_percent("NO VOC LISTED") is None
    sku_ok = Sku("L2", "00012345678905", "Spray Lubricant", "B", "lubricant", "VOC: 15%", False, False, 12, 1.0, 8.0)
    assert evaluate_voc(sku_ok, "CA", datetime(2026, 1, 1)).verdict == Verdict.KEEP
