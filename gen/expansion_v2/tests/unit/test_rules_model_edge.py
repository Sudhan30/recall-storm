"""Edge case tests for recallstorm.rules.model."""
from recallstorm.rules.model import RuleSet, rule_by_id, rules_for_state


def test_rules_model_edge():
    empty = RuleSet([])
    assert rule_by_id(empty, "MISSING") is None
    assert rules_for_state(empty, "CA") == []
