"""Edge case tests for recallstorm.states.ca_prop65_warnings."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.states.ca_prop65_warnings import (
    build_prop65_consent_judgment_rule,
    calculate_prop65_daily_madl_ug,
)


def test_ca_prop65_warnings_edge():
    with pytest.raises(DataValidationError):
        calculate_prop65_daily_madl_ug(-0.1)
    with pytest.raises(DataValidationError):
        build_prop65_consent_judgment_rule("CJ1", 0.0)
