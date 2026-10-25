"""Edge tests for recallstorm.route.returns."""
import pytest
from contract import Sku
from recallstorm.route.returns import (
    case_cube,
    case_weight,
    validate_returns,
)


def test_returns_edge():
    sku = Sku("S1", "00012345678905", "Candy", "B", "candy", "RED 3", True, False, 12, 2.0, 10.0)
    with pytest.raises(ValueError):
        case_cube(sku, -1)
    with pytest.raises(ValueError):
        case_weight(sku, -1)
    assert validate_returns({("WM1", "S1"): 5}, []) != []
