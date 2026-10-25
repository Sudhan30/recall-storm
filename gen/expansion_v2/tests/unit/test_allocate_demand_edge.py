"""Edge case tests for recallstorm.allocate.demand."""
from recallstorm.allocate.demand import demand_cases, substitute_for_sku


def test_allocate_demand_edge():
    assert demand_cases(0, 12) == 0
    assert demand_cases(-5, 12) == 0
    assert substitute_for_sku("MISSING", {}) is None
