"""Edge case tests for recallstorm.recall_lots.lot_pattern_matcher."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.recall_lots.lot_pattern_matcher import evaluate_julian_date_lot, expand_hyphenated_lot_span


def test_lot_pattern_matcher_edge():
    with pytest.raises(DataValidationError):
        evaluate_julian_date_lot("12")
    with pytest.raises(DataValidationError):
        expand_hyphenated_lot_span("L", 10, 5)
