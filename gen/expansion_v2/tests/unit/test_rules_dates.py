"""Unit tests for recallstorm.rules.dates."""
from datetime import datetime
from contract import Rule, Store, StoreFormat
from recallstorm.rules.dates import (
    days_until_effective,
    deadline_for_store,
    deadlines_by_tz,
    effective_at,
    first_prohibited_instant,
    is_prohibited_at,
    local_deadline,
    next_effective_rule,
    sell_through_allowed,
)


def test_rules_dates():
    r = Rule("CA_AB418_RED3", "RED3", ("Red 3",), ("CA",), ("food",), datetime(2027, 1, 1, 0, 0, 0), "c", "t")
    before = datetime.fromisoformat("2026-12-31T23:59:59-08:00")
    exact = datetime.fromisoformat("2027-01-01T00:00:00-08:00")
    assert not is_prohibited_at(r, before)
    assert sell_through_allowed(r, before)
    assert is_prohibited_at(r, exact)
    assert not sell_through_allowed(r, exact)
    assert days_until_effective(r, exact) == 0.0
    assert effective_at(r, "America/Los_Angeles").tzinfo is not None
    assert first_prohibited_instant([r]) == datetime(2027, 1, 1, 0, 0, 0)
    st = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    assert deadline_for_store(r, st) == local_deadline(r, "America/Los_Angeles")
    d_tz = deadlines_by_tz(r, ["America/Los_Angeles", "America/New_York"])
    assert d_tz["America/Los_Angeles"].endswith("-08:00")
    assert d_tz["America/New_York"].endswith("-05:00")
    assert next_effective_rule([r], before) == r
