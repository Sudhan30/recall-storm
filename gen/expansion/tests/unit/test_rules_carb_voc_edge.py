"""Edge tests for recallstorm.rules.carb_voc."""
from datetime import datetime, timezone
import pytest
from contract import Sku, Verdict
from recallstorm.rules.carb_voc import (
    evaluate_voc,
    parse_voc_percent,
)


def test_carb_voc_edge():
    assert parse_voc_percent("NO VOC MENTION") is None
    sku = Sku("LUB2", "00012345678905", "Low VOC Lubricant", "B", "lubricant", "VOC: 8%", False, False, 12, 1.0, 8.0)
    assert evaluate_voc(sku, "CA", datetime(2026, 6, 1, tzinfo=timezone.utc)).verdict == Verdict.KEEP
    with pytest.raises(TypeError):
        evaluate_voc("not_sku", "CA", datetime(2026, 6, 1))  # type: ignore[arg-type]
