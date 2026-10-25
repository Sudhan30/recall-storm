"""Edge tests for recallstorm.ingest.planogram."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.ingest.planogram import (
    location_from_code,
    parse_planogram_row,
    shelf_positions,
)


def test_planogram_edge():
    with pytest.raises(DataValidationError):
        location_from_code("BAD-CODE")
    with pytest.raises(DataValidationError):
        parse_planogram_row({"store_id": "S1"})
    with pytest.raises(ValueError):
        shelf_positions("A01", 0)
