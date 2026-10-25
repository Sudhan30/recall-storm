"""Edge case tests for recallstorm.ingest.usda_fdc."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.ingest.usda_fdc import fdc_gtin, fdc_is_food, parse_fdc_food


def test_usda_fdc_edge():
    with pytest.raises(DataValidationError):
        parse_fdc_food({})
    assert len(fdc_gtin({"fdcId": 99})) == 14
    assert not fdc_is_food({"brandedFoodCategory": "Cough Syrup Drug"})
