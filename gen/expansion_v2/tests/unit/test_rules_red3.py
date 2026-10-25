"""Unit tests for recallstorm.rules.red3."""
from datetime import datetime
from contract import Sku, Verdict
from recallstorm.rules.red3 import (
    RED3_RULE_IDS,
    evaluate_red3,
    red3_aliases,
    red3_clause,
    red3_deadline,
    red3_evidence,
    red3_rationale,
    red3_rules,
    red3_scope,
)


def test_red3_evaluation():
    rules = red3_rules()
    assert len(RED3_RULE_IDS) == 3
    assert "E127" in red3_aliases()
    assert "109025" in red3_clause("CA_AB418_RED3")
    assert red3_deadline("CA") == datetime(2027, 1, 1)
    assert red3_deadline("NY") == datetime(2027, 1, 15)
    assert red3_deadline("CA", is_drug=True) == datetime(2028, 1, 18)

    sku = Sku("S1", "07502264930572", "Sprinkles", "B", "baking", "SUGAR, FD&C RED #3, SALT", True, False, 6, 2.0, 10.0)
    assert red3_scope(sku, rules[0]) is True

    # 2027-01-05 in CA: CA_AB418_RED3 applies; in TX: not yet effective until Jan 15!
    d_ca = evaluate_red3(sku, rules, "CA", datetime.fromisoformat("2027-01-05T10:00:00-08:00"))
    assert d_ca.verdict == Verdict.PULL and d_ca.rule_ids == ("CA_AB418_RED3",)
    d_tx = evaluate_red3(sku, rules, "TX", datetime.fromisoformat("2027-01-05T10:00:00-06:00"))
    assert d_tx.verdict == Verdict.KEEP

    # 2027-01-16 in TX: FDA_RED3_FOOD applies!
    d_tx2 = evaluate_red3(sku, rules, "TX", datetime.fromisoformat("2027-01-16T10:00:00-06:00"))
    assert d_tx2.verdict == Verdict.PULL and d_tx2.rule_ids == ("FDA_RED3_FOOD",)
    assert "FD&C Red No. 3" in red3_rationale(sku, None, ()) or "RED3" in red3_rationale(sku, None, ())
