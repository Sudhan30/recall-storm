"""Unit tests for recallstorm.adjudicate.audit."""
from contract import DecidedBy, SkuDecision, Verdict
from recallstorm.adjudicate.audit import (
    AuditTrail,
    audit_diff,
    audit_summary,
    audit_to_records,
    decisions_by_source,
    overrides_by_user,
    record_decision,
    record_override,
    verify_audit,
)
from recallstorm.adjudicate.overrides import Override


def test_audit_trail():
    t1 = AuditTrail()
    d1 = SkuDecision("S1", Verdict.PULL, "RED3", "Red 3", 0, 5, ("CA_AB418_RED3",), DecidedBy.RULE, "r")
    ov = Override("S1", Verdict.KEEP, "LAB_COA_VERIFIED", "bob")
    record_decision(t1, d1)
    record_override(t1, ov)
    assert decisions_by_source(t1)["RULE"] == 1
    assert overrides_by_user(t1)["bob"] == 1
    assert len(audit_to_records(t1)) == 2
    assert audit_summary(t1)["total_decisions"] == 1
    assert verify_audit(t1) is True

    t2 = AuditTrail([SkuDecision("S1", Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, "r")])
    diff = audit_diff(t1, t2)
    assert diff["changed_count"] == 1
