"""Edge case tests for recallstorm.adjudicate.audit."""
from contract import DecidedBy, SkuDecision, Verdict
from recallstorm.adjudicate.audit import AuditTrail, audit_summary, verify_audit


def test_audit_edge():
    empty = AuditTrail()
    assert audit_summary(empty)["total_decisions"] == 0
    bad = AuditTrail([SkuDecision("", Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, "")])
    assert verify_audit(bad) is False
