"""Property tests for recallstorm.governance.audit_evidence_packs."""
from recallstorm.governance.audit_evidence_packs import compute_sha256_merkle_root_for_evidence


def test_merkle_root_order_invariance():
    items = [f"EVD-{i}" for i in range(15)]
    assert compute_sha256_merkle_root_for_evidence(items) == compute_sha256_merkle_root_for_evidence(list(reversed(items)))
