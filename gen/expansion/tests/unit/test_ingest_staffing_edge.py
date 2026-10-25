"""Edge tests for recallstorm.ingest.staffing."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.ingest.staffing import (
    parse_roster_row,
    parse_shift,
)


def test_staffing_edge():
    with pytest.raises(DataValidationError):
        parse_roster_row({})
    with pytest.raises(DataValidationError):
        parse_roster_row({"associate_id": "A1", "is_floater": False})
    with pytest.raises(DataValidationError):
        parse_shift("2026-12-31T06:00:00", "2026-12-30T22:00:00")
