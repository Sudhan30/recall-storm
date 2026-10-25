"""Edge case tests for recallstorm.vendor.supplier_scorecards."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.vendor.supplier_scorecards import (
    calculate_recall_frequency_severity_index,
    trigger_probationary_business_review,
)


def test_supplier_scorecards_edge():
    with pytest.raises(DataValidationError):
        calculate_recall_frequency_severity_index(-1, 0)
    with pytest.raises(DataValidationError):
        trigger_probationary_business_review("V1", 120.0)
