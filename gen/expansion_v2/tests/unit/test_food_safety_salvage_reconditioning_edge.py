"""Edge case tests for recallstorm.food_safety.salvage_reconditioning."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.food_safety.salvage_reconditioning import (
    record_rework_yield_shrinkage,
    segregate_non_salvageable_leakers,
)


def test_salvage_reconditioning_edge():
    with pytest.raises(DataValidationError):
        segregate_non_salvageable_leakers(5, 10)
    with pytest.raises(DataValidationError):
        record_rework_yield_shrinkage(10, 20)
