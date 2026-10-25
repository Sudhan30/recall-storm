"""Property tests for recallstorm.governance.approvals_workflow."""
from recallstorm.governance.approvals_workflow import capture_cryptographic_digital_signatures


def test_digital_signature_determinism():
    s1 = capture_cryptographic_digital_signatures("VP1", "LOCK", "2026-12-30T18:00:00Z")
    s2 = capture_cryptographic_digital_signatures("VP1", "LOCK", "2026-12-30T18:00:00Z")
    s3 = capture_cryptographic_digital_signatures("VP2", "LOCK", "2026-12-30T18:00:00Z")
    assert s1 == s2 and s1 != s3
