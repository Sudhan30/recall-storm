"""Edge tests for recallstorm.allocate.demand."""
from recallstorm.allocate.demand import (
    demand_cases,
    substitute_for_sku,
    total_demand,
)


def test_demand_edge():
    assert demand_cases(-5, 12) == 0
    assert substitute_for_sku("MISSING", {}) is None
    assert total_demand({}) == 0
