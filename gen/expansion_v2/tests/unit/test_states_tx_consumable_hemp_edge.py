"""Edge case tests for recallstorm.states.tx_consumable_hemp."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.states.tx_consumable_hemp import calculate_tx_hemp_tax_hold, check_tx_delta9_thc_pct


def test_tx_consumable_hemp_edge():
    with pytest.raises(DataValidationError):
        check_tx_delta9_thc_pct(-0.1)
    with pytest.raises(DataValidationError):
        calculate_tx_hemp_tax_hold(-5, 10.0)
