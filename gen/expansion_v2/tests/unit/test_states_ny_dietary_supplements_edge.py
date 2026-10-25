"""Edge case tests for recallstorm.states.ny_dietary_supplements."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.states.ny_dietary_supplements import (
    audit_ny_self_checkout_block,
    is_restricted_ny_supplement,
    verify_ny_pos_id_prompt,
)


def test_ny_dietary_supplements_edge():
    with pytest.raises(DataValidationError):
        is_restricted_ny_supplement("")
    with pytest.raises(DataValidationError):
        verify_ny_pos_id_prompt("S1", -5)
    with pytest.raises(DataValidationError):
        audit_ny_self_checkout_block("WM1", -1)
