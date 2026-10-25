"""Unit tests for recallstorm.rules.engine."""
from datetime import datetime, timezone
from contract import DecidedBy, Sku, SkuDecision, Verdict
from recallstorm.rules.engine import (
    RuleEngine,
    decision_counts,
    decision_to_record,
    evaluate_many,
    evaluate_sku,
    explain_decision,
    merge_decisions,
    strictest_decision,
)
from recallstorm.rules.red3 import red3_rules


def test_evaluate_sku_and_engine():
    rules = red3_rules()
    engine = RuleEngine(tuple(rules), "CA")
    at = datetime(2027, 1, 2, tzinfo=timezone.utc)

    s_pull = Sku("FDC1034191", "07502264930572", "Sprinkles", "B", "candy", "SUGAR, FD&C RED #3, FD&C RED #40.", True, False, 6, 2.0, 10.0)
    s_keep = Sku("FDC1913788", "00811033712026", "Cherries", "B", "fruit", "CHERRIES, WATER, FD&C RED #40.", True, False, 12, 1.4, 4.6)
    s_hold = Sku("U1", "00012345678905", "Frosting", "B", "baking", "SUGAR, ARTIFICIAL COLOR.", True, False, 12, 1.0, 5.0)

    d_pull = engine.evaluate(s_pull, at)
    assert d_pull.verdict == Verdict.PULL
    assert s_pull.ingredients[d_pull.match_start:d_pull.match_end] == d_pull.match_text

    d_keep = evaluate_sku(s_keep, rules, "CA", at)
    assert d_keep.verdict == Verdict.KEEP

    d_hold = evaluate_sku(s_hold, rules, "CA", at)
    assert d_hold.verdict == Verdict.HOLD_VERIFY

    many = evaluate_many([s_pull, s_keep, s_hold], rules, "CA", at)
    counts = decision_counts(many)
    assert counts == {"PULL": 1, "KEEP": 1, "HOLD_VERIFY": 1}

    assert strictest_decision(d_keep, d_pull) == d_pull
    merged = merge_decisions([d_keep, d_pull])
    assert merged.verdict == Verdict.PULL

    rec = decision_to_record(d_pull, s_pull, rules, "EVD-1")
    assert rec["type"] == "sku_verdict"
    assert rec["verdict"] == "PULL"
    assert "PULL" in explain_decision(d_pull)
