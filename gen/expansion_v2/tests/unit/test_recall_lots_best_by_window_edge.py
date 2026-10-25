"""Edge case tests for recallstorm.recall_lots.best_by_window."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.recall_lots.best_by_window import (
    convert_julian_to_calendar_date,
    parse_stamped_date_string,
    validate_window_chronology,
)


def test_best_by_window_edge():
    with pytest.raises(DataValidationError):
        parse_stamped_date_string("NOT_A_DATE")
    with pytest.raises(DataValidationError):
        convert_julian_to_calendar_date(2026, 400)
    with pytest.raises(DataValidationError):
        validate_window_chronology("2026-12-31", "2026-01-01")
