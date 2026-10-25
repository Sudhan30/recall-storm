"""Edge case tests for recallstorm.food_safety.foreign_material."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.food_safety.foreign_material import (
    calculate_complaint_per_million_units,
    check_fda_hard_sharp_7mm_rule,
)


def test_foreign_material_edge():
    with pytest.raises(DataValidationError):
        check_fda_hard_sharp_7mm_rule(-1.0)
    with pytest.raises(DataValidationError):
        calculate_complaint_per_million_units(5, 0)
