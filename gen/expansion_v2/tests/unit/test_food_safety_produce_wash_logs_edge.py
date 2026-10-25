"""Edge case tests for recallstorm.food_safety.produce_wash_logs."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.food_safety.produce_wash_logs import (
    log_wash_tank_water_temp_diff,
    verify_peracetic_acid_ppm_range,
)


def test_produce_wash_logs_edge():
    # Cold water on warm tomatoes (>10F colder) -> unsafe infiltration risk
    assert log_wash_tank_water_temp_diff(45.0, 70.0)["safe"] is False
    with pytest.raises(DataValidationError):
        verify_peracetic_acid_ppm_range(-5.0)
