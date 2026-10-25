"""Edge tests for recallstorm.labor.shifts."""
from datetime import datetime, timezone
import pytest
from contract import Associate
from recallstorm.labor.shifts import (
    clamp_to_shift,
    shift_window,
)


def test_shifts_edge():
    s = datetime(2026, 12, 30, 22, 0, tzinfo=timezone.utc)
    e = datetime(2026, 12, 31, 6, 0, tzinfo=timezone.utc)
    dl_early = datetime(2026, 12, 31, 2, 0, tzinfo=timezone.utc)
    a1 = Associate("A1", "WM1", "D01", False, s, e)
    _, ce = clamp_to_shift(a1, dl_early)
    assert ce < dl_early
    with pytest.raises(TypeError):
        shift_window("not_assoc")  # type: ignore[arg-type]
