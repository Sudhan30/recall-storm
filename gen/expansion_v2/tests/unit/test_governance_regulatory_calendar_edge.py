"""Edge case tests for recallstorm.governance.regulatory_calendar."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.governance.regulatory_calendar import (
    calculate_working_days_to_mandatory_ban,
    schedule_t_minus_90_day_readiness_drills,
)


def test_regulatory_calendar_edge():
    with pytest.raises(DataValidationError):
        calculate_working_days_to_mandatory_ban("2027-01-10", "2027-01-01")
    with pytest.raises(DataValidationError):
        schedule_t_minus_90_day_readiness_drills("2027-01-01", 0)
