"""Edge case tests for recallstorm.states.wv_kratom_hemp_act."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.states.wv_kratom_hemp_act import calculate_wv_unregistered_penalty, check_wv_mitragynine_limit


def test_wv_kratom_hemp_act_edge():
    with pytest.raises(DataValidationError):
        check_wv_mitragynine_limit(-1.0)
    with pytest.raises(DataValidationError):
        calculate_wv_unregistered_penalty(-5)
