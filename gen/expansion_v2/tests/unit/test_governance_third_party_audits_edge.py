"""Edge case tests for recallstorm.governance.third_party_audits."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.governance.third_party_audits import (
    grant_time_boxed_auditor_read_only_access,
    score_banner_integrity_gap_percentage,
)


def test_third_party_audits_edge():
    with pytest.raises(DataValidationError):
        grant_time_boxed_auditor_read_only_access("AUD1", 100)
    with pytest.raises(DataValidationError):
        score_banner_integrity_gap_percentage(10, 5)
