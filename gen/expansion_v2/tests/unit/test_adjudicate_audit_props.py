"""Property tests for recallstorm.adjudicate.audit."""
from contract import DecidedBy, SkuDecision, Verdict
from recallstorm.adjudicate.audit import AuditTrail, audit_diff, record_decision


def test_audit_self_diff_is_zero():
    t = AuditTrail()
    for i in range(15):
        record_decision(t, SkuDecision(f"S{i}", Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, ""))
    assert audit_diff(t, t)["changed_count"] == 0
