"""Edge case tests for recallstorm.gs1.lots."""
import pytest
from recallstorm.gs1.lots import lot_in_range, lot_matches_recall, parse_lot_code


def test_gs1_lots_edge():
    with pytest.raises(ValueError):
        parse_lot_code("   ")
    assert lot_in_range("", "A", "B") is False
    assert lot_matches_recall("", ["A"]) is False
