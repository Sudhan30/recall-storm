"""Unit tests for recallstorm.core.clock."""
from datetime import datetime, timezone
from recallstorm.core.clock import (
    clamp_window,
    from_local,
    is_before_deadline,
    iso_with_offset,
    local_wall,
    minutes_between,
    naive_local,
    to_local,
    window_overlaps,
)


def test_timezone_conversions():
    utc_dt = datetime(2027, 1, 1, 7, 0, tzinfo=timezone.utc)
    la_dt = to_local(utc_dt, "America/Los_Angeles")
    assert la_dt.hour == 23
    assert la_dt.day == 31
    wall = local_wall(utc_dt, "America/Los_Angeles")
    assert wall.tzinfo is None
    assert wall == naive_local(utc_dt, "America/Los_Angeles")
    aware = from_local(wall, "America/Los_Angeles")
    assert iso_with_offset(aware).endswith("-08:00")


def test_deadline_and_windows():
    d1 = "2026-12-31T23:59:00-08:00"
    dl = "2027-01-01T00:00:00-08:00"
    assert is_before_deadline(d1, dl) is True
    assert is_before_deadline(dl, dl) is False
    assert minutes_between(d1, dl) == 1.0
    assert window_overlaps([d1, dl], ["2026-12-31T23:30:00-08:00", "2026-12-31T23:59:30-08:00"]) is True


def test_clamp_window():
    b_s = datetime.fromisoformat("2026-12-30T22:00:00-08:00")
    b_e = datetime.fromisoformat("2026-12-31T06:00:00-08:00")
    w_s = datetime.fromisoformat("2026-12-30T20:00:00-08:00")
    w_e = datetime.fromisoformat("2026-12-31T08:00:00-08:00")
    cs, ce = clamp_window((w_s, w_e), (b_s, b_e))
    assert cs == b_s
    assert ce == b_e
