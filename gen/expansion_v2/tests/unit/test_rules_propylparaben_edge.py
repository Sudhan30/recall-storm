"""Edge case tests for recallstorm.rules.propylparaben."""
from datetime import datetime
from contract import Sku, Verdict
from recallstorm.rules.propylparaben import evaluate_propylparaben


def test_propylparaben_edge():
    sku = Sku("P1", "00012345678905", "Lotion", "B", "cosmetic", "PROPYLPARABEN", False, False, 12, 1.0, 5.0)
    assert evaluate_propylparaben(sku, "CA", datetime(2027, 1, 1)).verdict == Verdict.KEEP
    food_sku = Sku("P2", "00012345678905", "Cake", "B", "bakery", "SUGAR, WATER", True, False, 12, 1.0, 5.0)
    assert evaluate_propylparaben(food_sku, "CA", datetime(2027, 1, 1)).verdict == Verdict.KEEP
