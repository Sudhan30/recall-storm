"""Edge case tests for recallstorm.food_safety.water_ice_safety."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.food_safety.water_ice_safety import (
    authorize_water_system_reopen,
    schedule_carbon_filter_replacement,
)


def test_water_ice_safety_edge():
    assert authorize_water_system_reopen("WM1", True, False)["reopened"] is False
    with pytest.raises(DataValidationError):
        schedule_carbon_filter_replacement("WM1", 0)
