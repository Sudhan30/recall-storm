"""Edge case tests for recallstorm.analytics.simulation_calibration."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.analytics.simulation_calibration import (
    fit_lot_inspection_time_distributions,
    update_monte_carlo_prior_probabilities,
)


def test_simulation_calibration_edge():
    with pytest.raises(DataValidationError):
        fit_lot_inspection_time_distributions([])
    with pytest.raises(DataValidationError):
        update_monte_carlo_prior_probabilities(1.5, 0.5)
