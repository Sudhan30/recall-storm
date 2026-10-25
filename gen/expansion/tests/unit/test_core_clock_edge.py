"""Edge tests for recallstorm.core.clock."""
from datetime import datetime
import pytest
from recallstorm.core.clock import (
    clamp_window,
    iso_with_offset,
    to_local,
    window_overlaps,
)
from recallstorm.core.errors import DataValidationError


def test_unknown_timezone():
    with pytest.raises(DataValidationError):
        to_local(datetime(2027, 1, 1), "Invalid/Zone")


def test_adjacent_windows_do_not_overlap():
    w1 = ["2026-12-30T22:00:00-08:00", "2026-12-30T23:00:00-08:00"]
    w2 = ["2026-12-30T23:00:00-08:00", "2026-12-31T00:00:00-08:00"]
    assert window_overlaps(w1, w2) is False


def test_naive_iso_with_offset():
    dt = datetime(2026, 12, 30, 22, 0, 0)
    assert iso_with_offset(dt, "America/Los_Angeles") == "2026-12-30T22:00:00-08:00"


def test_invalid_bounds():
    dt = datetime(2026, 12, 30, 22, 0, 0)
    with pytest.raises(ValueError):
        clamp_window((dt, dt), (dt, dt))
