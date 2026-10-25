"""Edge case tests for recallstorm.food_safety.consumer_complaints."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.food_safety.consumer_complaints import (
    calculate_incubation_period_match,
    ingest_call_center_symptom_log,
)


def test_consumer_complaints_edge():
    with pytest.raises(DataValidationError):
        ingest_call_center_symptom_log("T1", [])
    with pytest.raises(DataValidationError):
        calculate_incubation_period_match(-5.0)
