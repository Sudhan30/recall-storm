"""Edge case tests for recallstorm.analytics.executive_briefings."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.analytics.executive_briefings import (
    project_estimated_time_to_full_containment,
    synthesize_hourly_war_room_situation_report,
)


def test_executive_briefings_edge():
    with pytest.raises(DataValidationError):
        synthesize_hourly_war_room_situation_report("R1", 150.0)
    with pytest.raises(DataValidationError):
        project_estimated_time_to_full_containment(10, 0.0)
