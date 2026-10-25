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
    dec = SkuDecision("S1", Verdict.HOLD_VERIFY, "RED3", None, None, None, ("CA_AB418_RED3",), DecidedBy.RULE, "r")
    ov = Override("S1", Verdict.KEEP, "VENDOR_COA_VERIFIED", "alice")
    record_decision(t1, dec, "2026-12-30T19:00:00-08:00")
    record_override(t1, ov, "2026-12-30T19:05:00-08:00")
    assert len(audit_to_records(t1)) == 2
    assert decisions_by_source(t1) == {"RULE": 1}
    assert overrides_by_user(t1) == {"alice": 1}
    assert audit_summary(t1)["total_entries"] == 2
    assert verify_audit(t1) is True

    t2 = AuditTrail()
    record_decision(t2, dec, "2026-12-30T19:00:00-08:00")
    diff = audit_diff(t1, t2)
    assert diff["changed_count"] == 1
