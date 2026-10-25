"""Edge tests for recallstorm.rules.engine."""
from datetime import datetime, timezone
import pytest
from contract import DecidedBy, Sku, SkuDecision, Verdict
from recallstorm.rules.engine import (
    evaluate_sku,
    merge_decisions,
)
from recallstorm.rules.red3 import red3_rules


def test_engine_classifier_hook_and_errors():
    rules = red3_rules()
    at = datetime(2027, 1, 2, tzinfo=timezone.utc)
    s_hold = Sku("U1", "00012345678905", "Frosting", "B", "baking", "SUGAR, ARTIFICIAL COLOR.", True, False, 12, 1.0, 5.0)

    def custom_clf(sku, candidates):
        return SkuDecision(sku.sku_id, Verdict.HOLD_VERIFY, "RED3", None, None, None, tuple(r.rule_id for r in candidates), DecidedBy.MODEL, "Model classified HOLD")

    dec = evaluate_sku(s_hold, rules, "CA", at, classifier=custom_clf)
    assert dec.decided_by == DecidedBy.MODEL

    with pytest.raises(TypeError):
        evaluate_sku("not_sku", rules, "CA", at)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        merge_decisions([])
