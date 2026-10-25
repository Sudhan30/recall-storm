"""Edge tests for recallstorm.rules.potassium_bromate."""
from datetime import datetime, timezone
import pytest
from contract import Sku, Verdict
from recallstorm.rules.potassium_bromate import evaluate_bromate


def test_potassium_bromate_edge():
    sku = Sku("B1", "00012345678905", "Bread", "Brand", "bakery", "WHEAT FLOUR, POTASSIUM BROMATE", True, False, 12, 1.0, 5.0)
    before = evaluate_bromate(sku, datetime(2026, 6, 1, tzinfo=timezone.utc))
    assert before.verdict == Verdict.KEEP
    with pytest.raises(TypeError):
        evaluate_bromate("not_sku", datetime(2027, 1, 1))  # type: ignore[arg-type]
