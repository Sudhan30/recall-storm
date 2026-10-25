"""Edge case tests for recallstorm.states.wa_pfas_packaging."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.states.wa_pfas_packaging import (
    calculate_wa_packaging_fines,
    test_wa_fluorine_ppm_limit as run_fluorine_check,
)


def test_wa_pfas_packaging_edge():
    with pytest.raises(DataValidationError):
        run_fluorine_check(-1.0)
    with pytest.raises(DataValidationError):
        calculate_wa_packaging_fines(-1)
