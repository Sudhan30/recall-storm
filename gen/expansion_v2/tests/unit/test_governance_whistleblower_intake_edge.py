"""Edge case tests for recallstorm.governance.whistleblower_intake."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.governance.whistleblower_intake import (
    generate_audit_committee_ethics_summary,
    ingest_anonymous_backroom_bypass_tips,
)


def test_whistleblower_intake_edge():
    with pytest.raises(DataValidationError):
        ingest_anonymous_backroom_bypass_tips("WM1", "")
    with pytest.raises(DataValidationError):
        generate_audit_committee_ethics_summary(5, 10)
