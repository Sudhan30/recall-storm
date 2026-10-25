"""Edge tests for recallstorm.rules.pfas_mn."""
from datetime import datetime, timezone
import pytest
from contract import Sku, Verdict
from recallstorm.rules.pfas_mn import evaluate_pfas


def test_pfas_mn_edge():
    sku = Sku("PF2", "00012345678905", "Hammer", "B", "hardware", "STEEL, PTFE", False, False, 6, 1.0, 10.0)
    assert evaluate_pfas(sku, "MN", datetime(2026, 1, 1, tzinfo=timezone.utc)).verdict == Verdict.KEEP
    with pytest.raises(TypeError):
        evaluate_pfas("not_sku", "MN", datetime(2026, 1, 1))  # type: ignore[arg-type]
