"""Property tests for recallstorm.adjudicate.classifier."""
from contract import Sku, Verdict
from recallstorm.adjudicate.classifier import HeuristicClassifier
from recallstorm.rules.red3 import red3_rules


def test_heuristic_classifier_determinism():
    rules = red3_rules()[:1]
    clf = HeuristicClassifier()
    for i in range(15):
        sku = Sku(f"S{i}", "00012345678905", "Candy", "B", "candy", "SUGAR, ARTIFICIAL COLOR", True, False, 12, 1.0, 5.0)
        assert clf(sku, rules) == clf(sku, rules)
        assert clf(sku, rules).verdict == Verdict.HOLD_VERIFY
