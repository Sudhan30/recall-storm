"""Unit tests for recallstorm.governance.retention_policies."""
from recallstorm.governance.retention_policies import (
    LegalHoldManager,
    RecordRetentionEnforcer,
    apply_seven_year_fda_fsma_retention_rule,
    archive_cold_storage_jsonl_to_glacier_worm,
    audit_unauthorized_deletion_attempts,
    generate_records_management_compliance_cert,
    link_related_vendor_correspondence_to_hold,
    manage_gdpr_ccpa_pii_redaction_schedules,
    place_litigation_hold_on_injury_linked_lots,
    prevent_auto_purge_of_recall_epcis_events,
    track_retention_expiration_disposition_dates,
    verify_immutable_s3_object_lock_status,
)


def test_retention_policies():
    assert LegalHoldManager().status == "ACTIVE"
    assert RecordRetentionEnforcer().status == "ACTIVE"
    assert apply_seven_year_fda_fsma_retention_rule("2026-12-30", 7) == "2033-12-28"
    assert place_litigation_hold_on_injury_linked_lots("L1", "MAT1")["indefinite_hold"] is True
    assert prevent_auto_purge_of_recall_epcis_events("R1")["exempt_from_purge"] is True
    assert archive_cold_storage_jsonl_to_glacier_worm("RUN1")["worm_locked"] is True
    assert manage_gdpr_ccpa_pii_redaction_schedules(400, 365)["redact_pii_now"] is True
    assert verify_immutable_s3_object_lock_status("plan.jsonl", True)["immutable"] is True
    recs = [
        {"id": "R1", "retain_until": "2033-12-28", "litigation_hold": False},
        {"id": "R2", "retain_until": "2033-12-28", "litigation_hold": True},
    ]
    assert track_retention_expiration_disposition_dates(recs, "2034-01-01") == ["R1"]
    assert audit_unauthorized_deletion_attempts("U1", "REC1")["blocked"] is True
    assert link_related_vendor_correspondence_to_hold("MAT1", ["E1"])["count"] == 1
    assert generate_records_management_compliance_cert("R1")["certified"] is True
