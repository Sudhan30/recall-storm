"""Edge case tests for recallstorm.states.pa_synthetic_dyes."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.states.pa_synthetic_dyes import calculate_pa_pack_exposure, check_pa_dye_concentration


def test_pa_synthetic_dyes_edge():
    with pytest.raises(DataValidationError):
        check_pa_dye_concentration(-1.0)
    with pytest.raises(DataValidationError):
        calculate_pa_pack_exposure(-5, 4)
