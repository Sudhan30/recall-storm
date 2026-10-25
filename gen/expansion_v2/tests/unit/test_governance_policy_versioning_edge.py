"""Edge case tests for recallstorm.governance.policy_versioning."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.governance.policy_versioning import (
    manage_annual_sop_recertification_cycles,
    track_effective_dates_of_state_ban_modules,
)


def test_policy_versioning_edge():
    with pytest.raises(DataValidationError):
        track_effective_dates_of_state_ban_modules({})
    with pytest.raises(DataValidationError):
        manage_annual_sop_recertification_cycles("SOP1", -1)
