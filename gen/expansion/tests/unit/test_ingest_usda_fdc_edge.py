"""Edge tests for recallstorm.ingest.usda_fdc."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.ingest.usda_fdc import (
    fdc_gtin,
    fdc_is_food,
    normalize_brand,
    normalize_category,
    parse_fdc_food,
    parse_fdc_search,
)


def test_fdc_edge_cases():
    assert normalize_brand(None) == "Generic"
    assert normalize_category(None) == "other food"
    assert fdc_is_food({"brandedFoodCategory": "Ingested Drug Cough Syrup"}) is False
    assert len(fdc_gtin({"fdcId": 99})) == 14
    with pytest.raises(DataValidationError):
        parse_fdc_food({})
    with pytest.raises(DataValidationError):
        parse_fdc_search({})
