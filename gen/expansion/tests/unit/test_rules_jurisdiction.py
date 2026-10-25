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
    assert "CA" in state_codes()
    assert state_name("CA") == "California"
    assert jurisdictions_for_state("CA") == ("CA", "US")
    assert jurisdiction_chain("CA") == ["CA", "US"]
    assert jurisdiction_rank("CA") == 1
    assert jurisdiction_rank("US") == 2

    r_ca = Rule("R_CA", "RED3", ("Red 3",), ("CA",), ("food",), datetime(2027, 1, 1), "c", "s")
    r_us = Rule("R_US", "RED3", ("Red 3",), ("US",), ("food",), datetime(2027, 1, 15), "c", "s")
    assert federal_applies(r_us) is True
    assert applies_in_state(r_ca, "CA") is True
    assert applies_in_state(r_ca, "TX") is False
    assert applies_in_state(r_us, "TX") is True
    assert state_preempts(r_ca, "CA") is True
    assert resolve_jurisdictions([r_us, r_ca], "CA") == [r_ca, r_us]
