"""Property tests for recallstorm.rules.engine."""
from datetime import datetime
from contract import Sku, Verdict
from recallstorm.rules.engine import evaluate_sku
from recallstorm.rules.red3 import red3_rules


def test_evaluate_sku_determinism_and_date_boundary():
    rules = red3_rules()
    sku = Sku("S1", "07502264930572", "Sprinkles", "B", "baking", "SUGAR, FD&C RED #3, SALT.", True, False, 6, 2.0, 10.0)
    pre = datetime.fromisoformat("2026-12-31T23:59:59-08:00")
    post = datetime.fromisoformat("2027-01-01T00:00:00-08:00")
    assert evaluate_sku(sku, rules, "CA", pre).verdict == Verdict.KEEP
    assert evaluate_sku(sku, rules, "CA", post).verdict == Verdict.PULL
    assert evaluate_sku(sku, rules, "CA", post) == evaluate_sku(sku, rules, "CA", post)
