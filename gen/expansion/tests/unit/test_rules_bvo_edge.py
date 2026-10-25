"""Edge tests for recallstorm.rules.bvo."""
from datetime import datetime, timezone
import pytest
from contract import Sku, Verdict
from recallstorm.rules.bvo import evaluate_bvo_federal


def test_bvo_edge():
    sku = Sku("BV1", "00012345678905", "Soda", "B", "soda", "WATER, BVO", True, False, 12, 1.0, 5.0)
    assert evaluate_bvo_federal(sku, datetime(2024, 1, 1, tzinfo=timezone.utc)).verdict == Verdict.KEEP
    with pytest.raises(TypeError):
        evaluate_bvo_federal("not_sku", datetime(2026, 1, 1))  # type: ignore[arg-type]
