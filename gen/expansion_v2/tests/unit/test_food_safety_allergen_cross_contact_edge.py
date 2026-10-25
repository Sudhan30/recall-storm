"""Edge case tests for recallstorm.food_safety.allergen_cross_contact."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.food_safety.allergen_cross_contact import check_deli_slicer_cleaning_gap


def test_allergen_cross_contact_edge():
    with pytest.raises(DataValidationError):
        check_deli_slicer_cleaning_gap(-1.0)
