"""Edge tests for recallstorm.labor.compliance."""
from datetime import datetime, timezone
import pytest
from recallstorm.labor.compliance import (
    break_required,
    max_shift_minutes,
    meal_break_window,
    overtime_minutes,
)


def test_compliance_edge():
    dt = datetime(2026, 12, 30, 22, 0, tzinfo=timezone.utc)
    with pytest.raises(ValueError):
        max_shift_minutes("")
    with pytest.raises(ValueError):
        break_required(-1.0)
    with pytest.raises(ValueError):
        meal_break_window(dt, dt)
    with pytest.raises(ValueError):
        overtime_minutes(-5.0)
