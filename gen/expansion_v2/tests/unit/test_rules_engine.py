"""Unit tests for recallstorm.rules.engine."""
from datetime import datetime
from contract import DecidedBy, Sku, SkuDecision, Verdict
from recallstorm.core.jsonl import validate_record
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


def test_evaluate_sku_sample_cases():
    rules = red3_rules()
    at_ca = datetime.fromisoformat("2027-01-01T00:00:00-08:00")

    # 1. Explicit FD&C Red #3 -> PULL
    s_pull = Sku(
        "FDC1034191",
        "07502264930572",
        "Rainbow Sprinkles",
        "Brand",
        "baking",
        "SUGAR, FD&C RED #3, FD&C RED #40, SALT.",
        True,
        False,
        6,
        2.05,
        23.2,
    )
    d_pull = evaluate_sku(s_pull, rules, "CA", at_ca)
    assert d_pull.verdict == Verdict.PULL
    assert d_pull.additive == "RED3"
    assert s_pull.ingredients[d_pull.match_start : d_pull.match_end] == d_pull.match_text
    assert d_pull.rule_ids == ("CA_AB418_RED3",)

    # 2. E127 alias -> PULL
    s_e127 = Sku("VAR0021", "02000000000213", "Pretzels", "B", "snacks", "NONPAREILS (SUGAR, E127, RED 40).", True, False, 12, 1.8, 4.2)
    d_e127 = evaluate_sku(s_e127, rules, "CA", at_ca)
    assert d_e127.verdict == Verdict.PULL and d_e127.match_text == "E127"

    # 3. Bundle kit -> PULL
    s_kit = Sku(
        "VAR0141",
        "02000000001418",
        "Easter Kit",
        "B",
        "seasonal kits",
        "KIT CONTAINS: Pretzels: SUGAR, RED 3 POWDER | Cherries: CHERRIES, RED 40.",
        True,
        False,
        12,
        2.0,
        4.9,
    )
    d_kit = evaluate_sku(s_kit, rules, "CA", at_ca)
    assert d_kit.verdict == Verdict.PULL

    # 4. Decoy Red 40 / Red Pepper -> KEEP
    s_keep = Sku("FDC1913788", "00811033712026", "Cherries", "B", "baking", "CHERRIES, WATER, FD&C RED #40, RED PEPPER.", True, False, 12, 1.4, 4.6)
    d_keep = evaluate_sku(s_keep, rules, "CA", at_ca)
    assert d_keep.verdict == Verdict.KEEP

    # 5. Unclear generic color -> HOLD_VERIFY
    s_hold = Sku("UNC1", "00012345678905", "Mystery Candy", "B", "candy", "SUGAR, CORN SYRUP, ARTIFICIAL COLOR.", True, False, 12, 1.0, 5.0)
    d_hold = evaluate_sku(s_hold, rules, "CA", at_ca)
    assert d_hold.verdict == Verdict.HOLD_VERIFY

    many = evaluate_many([s_pull, s_keep, s_hold], rules, "CA", at_ca)
    counts = decision_counts(many)
    assert counts["PULL"] == 1 and counts["KEEP"] == 1 and counts["HOLD_VERIFY"] == 1
    assert strictest_decision(d_keep, d_pull) == d_pull
    assert merge_decisions([d_keep, d_pull]).verdict == Verdict.PULL
    rec = decision_to_record(s_pull, d_pull, rules)
    assert validate_record(rec) == []
    assert "PULL" in explain_decision(d_pull)
    eng = RuleEngine(rules, "CA")
    assert eng.evaluate(s_pull, at_ca) == d_pull
