"""Edge tests for recallstorm.adjudicate.audit."""
import pytest
from recallstorm.adjudicate.audit import (
    AuditTrail,
    record_decision,
    record_override,
    verify_audit,
)


def test_audit_edge():
    t = AuditTrail(entries=[{"kind": "INVALID"}])
    assert verify_audit(t) is False
    with pytest.raises(TypeError):
        record_decision(t, "not_dec")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        record_override(t, "not_ov")  # type: ignore[arg-type]
