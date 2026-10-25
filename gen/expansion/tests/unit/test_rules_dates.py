"""Unit tests for recallstorm.rules.dates."""
from datetime import datetime, timezone
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


def test_dates_and_timezones():
    rule = Rule("CA_AB418_RED3", "RED3", ("Red 3",), ("CA",), ("food",), datetime(2027, 1, 1, 0, 0, 0), "c", "s")
    # 2027-01-01 07:00 UTC is 2026-12-31 23:00 in America/Los_Angeles (before effective)
    utc_dt = datetime(2027, 1, 1, 7, 0, tzinfo=timezone.utc)
    assert effective_at(rule, utc_dt, "America/Los_Angeles") is False
    assert sell_through_allowed(rule, utc_dt, "America/Los_Angeles") is True
    assert effective_at(rule, utc_dt, "America/New_York") is True
    assert is_prohibited_at(rule, utc_dt, "America/New_York") is True
    assert days_until_effective(rule, utc_dt, "America/Los_Angeles") == 1

    inst = first_prohibited_instant(rule, "America/Los_Angeles")
    assert inst == local_deadline(rule, "America/Los_Angeles")
    store = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    assert deadline_for_store(rule, store) == inst
    by_tz = deadlines_by_tz(rule, ["America/Los_Angeles", "America/New_York"])
    assert by_tz["America/New_York"] < by_tz["America/Los_Angeles"]
    assert next_effective_rule([rule], utc_dt, "America/Los_Angeles") == rule
