"""Edge case tests for recallstorm.analytics.forecasting_exposure."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.analytics.forecasting_exposure import (
    model_time_of_day_pos_basket_velocity,
    project_total_financial_write_off_range,
)


def test_forecasting_exposure_edge():
    with pytest.raises(DataValidationError):
        model_time_of_day_pos_basket_velocity(25)
    with pytest.raises(DataValidationError):
        project_total_financial_write_off_range(20, 10, 5.0)
