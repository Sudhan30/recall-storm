"""Edge tests for recallstorm.gs1.lots."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.gs1.lots import (
    expiry_in_range,
    lot_in_range,
    normalize_lot,
    parse_lot_code,
)


def test_lots_edge():
    assert lot_in_range("SHORT", "L260001", "L260010") is False
    with pytest.raises(DataValidationError):
        normalize_lot("   ")
    with pytest.raises(DataValidationError):
        parse_lot_code("")
    with pytest.raises(ValueError):
        expiry_in_range("2026-11-01", "2026-12-01", "2026-10-01")
