"""Edge case tests for recallstorm.states.nj_lead_cadmium."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.states.nj_lead_cadmium import calculate_nj_daily_intake_exposure, check_nj_candy_lead_ppb


def test_nj_lead_cadmium_edge():
    with pytest.raises(DataValidationError):
        check_nj_candy_lead_ppb(-1.0)
    with pytest.raises(DataValidationError):
        calculate_nj_daily_intake_exposure(-5.0, 10.0)
