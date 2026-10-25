"""Edge case tests for recallstorm.governance.audit_evidence_packs."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.governance.audit_evidence_packs import (
    compute_sha256_merkle_root_for_evidence,
    verify_completeness_of_mandatory_artifacts,
)


def test_audit_evidence_packs_edge():
    with pytest.raises(DataValidationError):
        compute_sha256_merkle_root_for_evidence([])
    assert verify_completeness_of_mandatory_artifacts(set())["complete"] is False
