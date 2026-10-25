"""Edge tests for recallstorm.rules.ab418."""
from datetime import datetime, timezone
from contract import Sku, Verdict
from recallstorm.rules.ab418 import (
    ab418_clause,
    evaluate_bvo,
)


def test_ab418_edge():
    assert ab418_clause("UNKNOWN") == "Cal. Health & Safety Code 109025(a)"
    sku = Sku("S1", "00012345678905", "Soda", "B", "beverage", "WATER, BVO", True, False, 12, 1.0, 5.0)
    assert evaluate_bvo(sku, datetime(2026, 1, 1, tzinfo=timezone.utc)).verdict == Verdict.KEEP
