"""Edge case tests for recallstorm.states.vt_mercury_battery."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.states.vt_mercury_battery import calculate_vt_recycling_surcharge, check_vt_alkaline_mercury_ppm


def test_vt_mercury_battery_edge():
    with pytest.raises(DataValidationError):
        check_vt_alkaline_mercury_ppm(-1.0)
    with pytest.raises(DataValidationError):
        calculate_vt_recycling_surcharge(-5)
