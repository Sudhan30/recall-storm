"""Unit tests for recallstorm.rules.model."""
from datetime import datetime
from contract import Rule
from recallstorm.core.jsonl import write_jsonl
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


def test_rules_model(tmp_path):
    p = tmp_path / "rules.jsonl"
    write_jsonl(
        str(p),
        [
            {
                "rule_id": "CA_AB418_RED3",
                "additive": "RED3",
                "aliases": ["Red 3"],
                "jurisdictions": ["CA"],
                "applies_to": ["food"],
                "effective": "2027-01-01T00:00:00",
                "clause_ref": "Cal. HSC 109025",
                "source_text": "Ban Red 3",
            }
        ],
    )
    rs = load_rules(str(p))
    assert isinstance(rs, RuleSet)
    r = rule_by_id(rs, "CA_AB418_RED3")
    assert r is not None
    assert len(rules_for_state(rs, "CA")) == 1
    assert len(rules_for_additive(rs, "RED3")) == 1
    assert len(rules_for_product_type(rs, "food")) == 1
    assert effective_local(r, "America/Los_Angeles").tzinfo is not None
    assert rule_summary(r)["rule_id"] == "CA_AB418_RED3"
    assert len(ruleset_hash(rs)) == 16
