"""Edge case tests for recallstorm.analytics.labor_efficiency."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.analytics.labor_efficiency import (
    calculate_units_pulled_per_labor_minute,
    compare_actual_walk_path_to_optimal_tour,
)


def test_labor_efficiency_edge():
    with pytest.raises(DataValidationError):
        calculate_units_pulled_per_labor_minute(10, 0.0)
    with pytest.raises(DataValidationError):
        compare_actual_walk_path_to_optimal_tour(100.0, 200.0)
