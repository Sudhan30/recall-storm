"""Property tests for recallstorm.rules.ab418."""
from datetime import datetime
from contract import Sku, Verdict
from recallstorm.rules.ab418 import ab418_rules
from recallstorm.rules.engine import evaluate_sku


def test_ab418_rules_via_engine():
    rules = ab418_rules()
    t = datetime.fromisoformat("2027-01-01T00:00:00-08:00")
    for r in rules:
        sku = Sku(f"S_{r.additive}", "00012345678905", "Item", "B", "food", f"WATER, {r.aliases[0]}, SALT", True, False, 12, 1.0, 5.0)
        dec = evaluate_sku(sku, rules, "CA", t)
        assert dec.verdict == Verdict.PULL
        assert dec.additive == r.additive
