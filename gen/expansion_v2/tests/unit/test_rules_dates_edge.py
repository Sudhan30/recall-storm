"""Edge case tests for recallstorm.rules.dates."""
from datetime import datetime
from contract import Rule
from recallstorm.rules.dates import first_prohibited_instant, is_prohibited_at, next_effective_rule


def test_rules_dates_edge():
    assert first_prohibited_instant([]) is None
    r = Rule("R1", "RED3", ("Red 3",), ("US",), ("food",), datetime(2027, 1, 15, 0, 0, 0), "c", "t")
    # 2027-01-14 22:00 PST is 2027-01-15 01:00 EST -> prohibited in NY, allowed in LA!
    at_pst = datetime.fromisoformat("2027-01-14T22:00:00-08:00")
    assert not is_prohibited_at(r, at_pst, tz_name="America/Los_Angeles")
    assert is_prohibited_at(r, at_pst, tz_name="America/New_York")
    assert next_effective_rule([r], datetime(2028, 1, 1)) is None
