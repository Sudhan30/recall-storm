"""Edge case tests for recallstorm.route.returns."""
import pytest
from contract import Sku
from recallstorm.route.returns import case_cube, case_weight, validate_returns


def test_route_returns_edge():
    sku = Sku("S1", "00012345678905", "N", "B", "c", "I", True, False, 6, 2.0, 10.0)
    with pytest.raises(ValueError):
        case_cube(sku, -1)
    with pytest.raises(ValueError):
        case_weight(sku, -1)
    assert len(validate_returns({("WM1", "MISSING"): -2}, {"S1": sku})) == 2
