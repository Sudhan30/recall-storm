"""Edge case tests for recallstorm.governance.access_logs."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.governance.access_logs import (
    audit_third_party_auditor_portal_sessions,
    generate_siem_compatible_cef_security_logs,
)


def test_access_logs_edge():
    with pytest.raises(DataValidationError):
        audit_third_party_auditor_portal_sessions("AUD1", [])
    with pytest.raises(DataValidationError):
        generate_siem_compatible_cef_security_logs("EV", "U1", 99)
