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


def test_preemption_resolution():
    r_ca = Rule("CA_AB418_RED3", "RED3", ("Red 3",), ("CA",), ("food",), datetime(2027, 1, 1), "c1", "s1")
    r_us = Rule("FDA_RED3_FOOD", "RED3", ("Red 3",), ("US",), ("food",), datetime(2027, 1, 15), "c2", "s2")
    rules = [r_ca, r_us]
    res = PreemptionResolver(tuple(rules))
    assert len(res.rules) == 2
    assert federal_rule_for(rules, "RED3") == r_us
    assert state_rule_for(rules, "RED3", "CA") == r_ca
    assert stricter_rule(r_ca, r_us) == r_ca
    assert effective_conflict(r_ca, r_us) is True
    assert preemption_status(r_ca, r_us) == "STATE_EARLIER"
    active_jan2 = resolve_conflicts(rules, "CA", datetime(2027, 1, 2))
    assert active_jan2 == [r_ca]
    rep = preemption_report(rules, "CA")
    assert rep["additives"]["RED3"] == "STATE_EARLIER"
    mat = preemption_matrix(rules, ["CA", "TX"])
    assert mat["CA"] == ["CA_AB418_RED3", "FDA_RED3_FOOD"]
    assert mat["TX"] == ["FDA_RED3_FOOD"]
