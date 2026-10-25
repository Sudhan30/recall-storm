"""Property tests for recallstorm.rules.jurisdiction."""
from datetime import datetime
from contract import Rule
from recallstorm.rules.jurisdiction import applies_in_state, state_codes


def test_us_rule_applies_in_every_state():
    r_us = Rule("US_R", "RED3", ("Red 3",), ("US",), ("food",), datetime(2027, 1, 15), "c", "t")
    for code in state_codes():
        assert applies_in_state(r_us, code) is True
