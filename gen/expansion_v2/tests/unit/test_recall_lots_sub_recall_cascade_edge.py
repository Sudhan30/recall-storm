"""Edge case tests for recallstorm.recall_lots.sub_recall_cascade."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.recall_lots.sub_recall_cascade import calculate_generational_dilution_factor


def test_sub_recall_cascade_edge():
    with pytest.raises(DataValidationError):
        calculate_generational_dilution_factor(50.0, 10.0)
