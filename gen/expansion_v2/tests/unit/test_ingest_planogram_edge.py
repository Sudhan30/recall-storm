"""Edge case tests for recallstorm.ingest.planogram."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.ingest.planogram import bay_capacity, location_from_code, parse_planogram_row


def test_planogram_edge():
    with pytest.raises(DataValidationError):
        location_from_code("BADCODE")
    with pytest.raises(DataValidationError):
        location_from_code("A-1-2")
    with pytest.raises(DataValidationError):
        parse_planogram_row({})
    with pytest.raises(ValueError):
        bay_capacity(0, 1)
