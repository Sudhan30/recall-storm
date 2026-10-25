"""Property tests for recallstorm.governance.policy_versioning."""
from recallstorm.governance.policy_versioning import diff_rule_engine_thresholds_between_drills


def test_self_diff_is_empty():
    rules = {"A": 10.0, "B": 25.0}
    assert diff_rule_engine_thresholds_between_drills(rules, rules) == {}
