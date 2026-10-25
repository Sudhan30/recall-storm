"""Unit tests for recallstorm.rules.model."""
from recallstorm.rules.model import (
    RuleSet,
    effective_local,
    load_rules,
    rule_by_id,
    rule_summary,
    rules_for_additive,
    rules_for_product_type,
    rules_for_state,
    ruleset_hash,
)


def test_ruleset_model():
    rs = load_rules("data/rules.jsonl")
    assert isinstance(rs, RuleSet)
    assert len(rs.rules) >= 3
    r = rule_by_id(rs, "CA_AB418_RED3")
    assert r.additive == "RED3"
    assert len(rules_for_state(rs, "CA")) >= 3
    assert len(rules_for_state(rs, "TX")) >= 2
    assert len(rules_for_additive(rs, "RED3")) >= 3
    assert len(rules_for_product_type(rs, "ingested_drug")) >= 1
    eff = effective_local(r, "America/Los_Angeles")
    assert eff.tzinfo is not None
    assert rule_summary(r)["rule_id"] == "CA_AB418_RED3"
    assert len(ruleset_hash(rs)) == 16
