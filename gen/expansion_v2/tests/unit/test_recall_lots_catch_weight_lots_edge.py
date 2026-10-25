"""Edge case tests for recallstorm.recall_lots.catch_weight_lots."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.recall_lots.catch_weight_lots import (
    calculate_meat_chub_yield_loss,
    extract_embedded_price_weight_upc,
)


def test_catch_weight_lots_edge():
    with pytest.raises(DataValidationError):
        extract_embedded_price_weight_upc("012345678905")
    with pytest.raises(DataValidationError):
        calculate_meat_chub_yield_loss(10.0, 20.0)
