"""Edge case tests for recallstorm.rules.potassium_bromate."""
from datetime import datetime
from contract import Sku, Verdict
from recallstorm.rules.potassium_bromate import evaluate_bromate


def test_potassium_bromate_edge():
    sku = Sku("B1", "00012345678905", "Bread", "B", "bakery", "POTASSIUM BROMATE", True, False, 12, 1.0, 5.0)
    # Out of state -> KEEP
    assert evaluate_bromate(sku, "TX", datetime(2027, 1, 2)).verdict == Verdict.KEEP
    # Before effective -> KEEP
    assert evaluate_bromate(sku, "CA", datetime(2026, 12, 31, 23, 59)).verdict == Verdict.KEEP
