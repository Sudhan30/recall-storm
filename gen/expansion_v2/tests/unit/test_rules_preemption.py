"""Unit tests for recallstorm.rules.preemption."""
from datetime import datetime
from contract import Rule
from recallstorm.rules.preemption import (
    PreemptionResolver,
    effective_conflict,
    federal_rule_for,
    preemption_matrix,
    preemption_report,
    preemption_status,
    resolve_conflicts,
    state_rule_for,
    stricter_rule,
)


def test_preemption():
    r_ca = Rule("CA_AB418_RED3", "RED3", ("Red 3",), ("CA",), ("food",), datetime(2027, 1, 1), "ref", "txt")
    r_us = Rule("FDA_RED3_FOOD", "RED3", ("Red 3",), ("US",), ("food",), datetime(2027, 1, 15), "ref", "txt")
    rules = [r_ca, r_us]
    assert len(federal_rule_for("RED3", rules)) == 1
    assert len(state_rule_for("RED3", "CA", rules)) == 1
    assert stricter_rule(r_ca, r_us) == r_ca
    assert effective_conflict(r_ca, r_us) is True
    assert preemption_status(r_ca, r_us) == "STATE_EARLIER"
    assert len(resolve_conflicts(rules, "CA", datetime(2027, 1, 5))) == 1
    assert len(resolve_conflicts(rules, "CA", datetime(2027, 1, 20))) == 2
    rep = preemption_report(rules, "CA")
    assert rep["comparisons"][0]["status"] == "STATE_EARLIER"
    assert preemption_matrix(rules)["RED3"]["CA"] == "CA_AB418_RED3"
    res = PreemptionResolver(rules)
    assert len(res.resolve("CA", datetime(2027, 1, 2))) == 1
