"""Edge case tests for recallstorm.food_safety.haccp_deviations."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.food_safety.haccp_deviations import (
    evaluate_cooking_lethality_log,
    lock_affected_production_window,
)


def test_haccp_deviations_edge():
    with pytest.raises(DataValidationError):
        evaluate_cooking_lethality_log(-10.0)
    with pytest.raises(DataValidationError):
        lock_affected_production_window("L1", "2026-12-30T12:00", "2026-12-30T10:00")
