"""Unit tests for recallstorm.core.clock."""
from datetime import datetime
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


def test_clock_conversions():
    dt = datetime.fromisoformat("2026-12-30T18:00:00-08:00")
    ny = to_local(dt, "America/New_York")
    assert ny.hour == 21
    wall = local_wall(dt, "America/New_York")
    assert wall.tzinfo is None and wall.hour == 21
    assert naive_local(dt) == datetime(2026, 12, 30, 18, 0, 0)
    aware = from_local(datetime(2027, 1, 1, 0, 0), "America/Los_Angeles")
    assert iso_with_offset(aware).endswith("-08:00")

    deadline = datetime.fromisoformat("2027-01-01T00:00:00-08:00")
    assert is_before_deadline(dt, deadline)
    assert not is_before_deadline(deadline, deadline, strict=True)
    assert is_before_deadline(deadline, deadline, strict=False)
    assert minutes_between(dt, deadline) == 30 * 60.0


def test_windows():
    t0 = datetime.fromisoformat("2026-12-30T22:00:00-08:00")
    t1 = datetime.fromisoformat("2026-12-30T23:00:00-08:00")
    t2 = datetime.fromisoformat("2026-12-30T22:30:00-08:00")
    t3 = datetime.fromisoformat("2026-12-31T01:00:00-08:00")
    assert window_overlaps((t0, t1), (t2, t3))
    assert clamp_window((t0, t3), (t0, t1)) == (t0, t1)
