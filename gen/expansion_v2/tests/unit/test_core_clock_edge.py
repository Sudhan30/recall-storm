"""Edge case tests for recallstorm.core.clock."""
from datetime import datetime
import pytest
from recallstorm.core.clock import clamp_window, to_local, window_overlaps
from recallstorm.core.errors import DataValidationError


def test_clock_edge_cases():
    with pytest.raises(DataValidationError):
        to_local(datetime.now(), "Invalid/Timezone")
    t0 = datetime(2026, 12, 30, 10, 0)
    t1 = datetime(2026, 12, 30, 11, 0)
    t2 = datetime(2026, 12, 30, 12, 0)
    assert not window_overlaps((t0, t1), (t1, t2))
    assert clamp_window((t0, t1), (t1, t2)) is None
