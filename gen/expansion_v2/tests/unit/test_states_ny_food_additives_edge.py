"""Edge case tests for recallstorm.states.ny_food_additives."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.states.ny_food_additives import calculate_ny_civil_penalty, check_ny_ban_date, filter_ny_store_zips


def test_ny_food_additives_edge():
    with pytest.raises(DataValidationError):
        check_ny_ban_date("")
    with pytest.raises(DataValidationError):
        calculate_ny_civil_penalty(-1)
    with pytest.raises(DataValidationError):
        filter_ny_store_zips(None)  # type: ignore[arg-type]
