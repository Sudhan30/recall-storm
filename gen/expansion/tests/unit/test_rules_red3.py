"""Unit tests for recallstorm.rules.red3."""
from datetime import datetime, timezone
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
    assert len(RED3_RULE_IDS) == 3
    assert "E127" in red3_aliases()
    rules = red3_rules()
    assert "109025" in red3_clause("CA_AB418_RED3")
    assert red3_deadline("CA_AB418_RED3").year == 2027

    sku = Sku("FDC1034191", "07502264930572", "Sprinkles", "B", "candy", "SUGAR, FD&C RED #3, SALT", True, False, 6, 2.0, 10.0)
    assert red3_scope(sku, rules[0]) is True

    # CA on 2027-01-02 -> CA_AB418_RED3 active, FDA_RED3_FOOD not yet active
    dec = evaluate_red3(sku, rules, "CA", datetime(2027, 1, 2, tzinfo=timezone.utc))
    assert dec.verdict == Verdict.PULL
    assert dec.rule_ids == ("CA_AB418_RED3",)
    assert dec.match_text == "FD&C RED #3"
    assert "FD&C RED #3" in red3_rationale(sku, None, rules) or "No FD&C" in red3_rationale(sku, None, rules)

    # TX on 2027-01-02 -> KEEP
    dec_tx = evaluate_red3(sku, rules, "TX", datetime(2027, 1, 2, tzinfo=timezone.utc))
    assert dec_tx.verdict == Verdict.KEEP

    # TX on 2027-01-20 -> PULL via FDA_RED3_FOOD
    dec_tx_after = evaluate_red3(sku, rules, "TX", datetime(2027, 1, 20, tzinfo=timezone.utc))
    assert dec_tx_after.verdict == Verdict.PULL
    assert dec_tx_after.rule_ids == ("FDA_RED3_FOOD",)

    from recallstorm.aliases.detect import find_first_match
    m = find_first_match(sku.ingredients, "RED3")
    assert m is not None
    ev = red3_evidence(sku, rules[0], m)
    assert ev["sku_id"] == "FDC1034191"
