"""Unit tests for recallstorm.governance.audit_evidence_packs."""
from recallstorm.governance.audit_evidence_packs import (
    AuditBinderCompiler,
    TamperEvidentPackager,
    assemble_store_by_store_execution_dossier,
    attach_geotagged_quarantine_cage_photos,
    bundle_timestamped_pos_lock_confirmations,
    compute_sha256_merkle_root_for_evidence,
    cross_reference_fda_effectiveness_checks,
    export_encrypted_regulator_handoff_zip,
    generate_pdf_a_archival_compliance_binder,
    include_signed_destruction_witness_certs,
    verify_completeness_of_mandatory_artifacts,
    watermark_confidential_regulatory_exhibits,
)


def test_audit_evidence_packs():
    assert AuditBinderCompiler().status == "ACTIVE"
    assert TamperEvidentPackager().status == "ACTIVE"
    assert assemble_store_by_store_execution_dossier("R1", ["WM1"])["stores"] == ["WM1"]
    assert bundle_timestamped_pos_lock_confirmations("R1", 50)["lane_acks"] == 50
    assert attach_geotagged_quarantine_cage_photos("WM1", ["h1"])["photos"] == ["h1"]
    assert include_signed_destruction_witness_certs(["C2", "C1"]) == ["C1", "C2"]
    root = compute_sha256_merkle_root_for_evidence(["EV1", "EV2", "EV3"])
    assert len(root) == 16
    assert generate_pdf_a_archival_compliance_binder("R1", root)["format"] == "PDF/A-2b"
    assert cross_reference_fda_effectiveness_checks({"WM1", "WM2"}, {"WM1"}) is True
    assert verify_completeness_of_mandatory_artifacts({"POS_LOCK", "STORE_ATTESTATION", "DESTRUCTION_CERT"})["complete"] is True
    assert "CONFIDENTIAL" in watermark_confidential_regulatory_exhibits("EX1", "FDA")
    assert export_encrypted_regulator_handoff_zip("R1", "out.zip")["encrypted"] is True
