"""Edge case tests for recallstorm.rules.engine."""
from datetime import datetime
import pytest
from contract import DecidedBy, Sku, SkuDecision, Verdict
from recallstorm.rules.engine import evaluate_sku, merge_decisions
from recallstorm.rules.red3 import red3_rules


def test_engine_classifier_hook_and_errors():
    rules = red3_rules()
    at_ca = datetime.fromisoformat("2027-01-01T00:00:00-08:00")
    s_hold = Sku("UNC1", "00012345678905", "Candy", "B", "candy", "SUGAR, ARTIFICIAL COLOR.", True, False, 12, 1.0, 5.0)

    def custom_clf(sku, candidates):
        return SkuDecision(sku.sku_id, Verdict.HOLD_VERIFY, "RED3", None, None, None, tuple(r.rule_id for r in candidates), DecidedBy.MODEL, "Model flagged")

    dec = evaluate_sku(s_hold, rules, "CA", at_ca, classifier=custom_clf)
    assert dec.decided_by == DecidedBy.MODEL
    assert dec.verdict == Verdict.HOLD_VERIFY

    with pytest.raises(ValueError):
        merge_decisions([])
