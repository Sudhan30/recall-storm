"""Edge case tests for recallstorm.states.az_kratom_consumer_act."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.states.az_kratom_consumer_act import calculate_az_civil_forfeiture, verify_az_7_oh_fraction_limit


def test_az_kratom_consumer_act_edge():
    with pytest.raises(DataValidationError):
        verify_az_7_oh_fraction_limit(-0.5)
    with pytest.raises(DataValidationError):
        calculate_az_civil_forfeiture(-1)
