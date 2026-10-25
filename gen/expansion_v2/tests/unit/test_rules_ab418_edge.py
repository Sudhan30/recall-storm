"""Edge case tests for recallstorm.rules.ab418."""
from datetime import datetime
from contract import Sku, Verdict
from recallstorm.rules.ab418 import evaluate_bvo


def test_ab418_edge():
    s = Sku("S1", "00012345678905", "Soda", "B", "bev", "WATER, BVO", True, False, 12, 1.0, 5.0)
    assert evaluate_bvo(s, "OR", datetime(2027, 1, 1)).verdict == Verdict.KEEP
    assert evaluate_bvo(s, "CA", datetime(2026, 12, 31)).verdict == Verdict.KEEP
