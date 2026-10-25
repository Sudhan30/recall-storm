"""Edge case tests for recallstorm.comms.associate_briefings."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.comms.associate_briefings import (
    generate_five_minute_huddle_talking_points,
    record_huddle_attendance_badge_scans,
)


def test_associate_briefings_edge():
    with pytest.raises(DataValidationError):
        generate_five_minute_huddle_talking_points("R1", [])
    with pytest.raises(DataValidationError):
        record_huddle_attendance_badge_scans("WM1", [])
