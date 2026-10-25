"""Edge case tests for recallstorm.food_safety.temperature_holds."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.food_safety.temperature_holds import (
    authorize_disposition_after_review,
    parse_reefer_data_logger_csv,
)


def test_temperature_holds_edge():
    with pytest.raises(DataValidationError):
        parse_reefer_data_logger_csv("38.0, BAD")
    with pytest.raises(DataValidationError):
        authorize_disposition_after_review("H1", "UNKNOWN")
