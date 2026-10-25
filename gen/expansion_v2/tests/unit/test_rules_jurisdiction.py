"""Unit tests for recallstorm.rules.jurisdiction."""
from datetime import datetime
from contract import Rule
from recallstorm.rules.jurisdiction import (
    applies_in_state,
    federal_applies,
    jurisdiction_chain,
    jurisdiction_rank,
    jurisdictions_for_state,
    resolve_jurisdictions,
    state_codes,
    state_name,
    state_preempts,
)


def test_jurisdiction_functions():
    r_ca = Rule("CA_R", "RED3", ("Red 3",), ("CA",), ("food",), datetime(2027, 1, 1), "c", "t")
    r_us = Rule("US_R", "RED3", ("Red 3",), ("US",), ("food",), datetime(2027, 1, 15), "c", "t")
    assert jurisdictions_for_state("CA") == ("CA", "US")
    assert jurisdiction_chain("CA") == ["CA", "US"]
    assert applies_in_state(r_ca, "CA") is True
    assert applies_in_state(r_ca, "NY") is False
    assert applies_in_state(r_us, "NY") is True
    assert federal_applies(r_us) is True
    assert state_preempts(r_ca, r_us) is True
    assert jurisdiction_rank("CA") < jurisdiction_rank("US")
    resolved = resolve_jurisdictions([r_us, r_ca], "CA")
    assert resolved[0].rule_id == "CA_R"
    assert state_name("CA") == "California"
    assert "CA" in state_codes()
