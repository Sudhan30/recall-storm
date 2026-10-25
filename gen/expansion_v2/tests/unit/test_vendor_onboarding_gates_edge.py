"""Edge case tests for recallstorm.vendor.onboarding_gates."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.vendor.onboarding_gates import (
    require_state_specific_regulatory_attestation,
    screen_new_item_setup_for_banned_additives,
)


def test_onboarding_gates_edge():
    assert screen_new_item_setup_for_banned_additives("WATER, SALT")["blocked"] is False
    with pytest.raises(DataValidationError):
        require_state_specific_regulatory_attestation("V1", [])
