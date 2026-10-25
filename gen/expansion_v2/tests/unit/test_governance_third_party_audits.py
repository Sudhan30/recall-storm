"""Unit tests for recallstorm.governance.third_party_audits."""
from recallstorm.governance.third_party_audits import (
    ExternalAuditorPortal,
    StoreWalkVerification,
    archive_independent_verification_certificates,
    benchmark_internal_vs_external_pass_rates,
    grant_time_boxed_auditor_read_only_access,
    ingest_third_party_mystery_shopper_scans,
    reconcile_external_audit_findings_with_self_report,
    schedule_unannounced_steritech_ecolab_checks,
    score_banner_integrity_gap_percentage,
    track_corrective_coaching_for_failed_stores,
    trigger_immediate_re_pull_on_auditor_find,
    verify_pulled_sku_absence_on_store_shelves,
)


def test_third_party_audits():
    assert ExternalAuditorPortal().status == "ACTIVE"
    assert StoreWalkVerification().status == "ACTIVE"
    assert schedule_unannounced_steritech_ecolab_checks(["WM2", "WM1"], 1) == ["WM1"]
    assert grant_time_boxed_auditor_read_only_access("AUD1", 8)["read_only"] is True
    assert ingest_third_party_mystery_shopper_scans("WM1", 0)["passed"] is True
    assert verify_pulled_sku_absence_on_store_shelves("WM1", "S1", 0)["absent"] is True
    assert reconcile_external_audit_findings_with_self_report(True, 3)["integrity_gap"] is True
    assert trigger_immediate_re_pull_on_auditor_find("WM1", "S1")["re_pull_dispatched"] is True
    assert score_banner_integrity_gap_percentage(2, 50) == 4.0
    assert track_corrective_coaching_for_failed_stores("WM1", True)["completed"] is True
    assert benchmark_internal_vs_external_pass_rates(99.0, 95.0) == 4.0
    assert archive_independent_verification_certificates("R1", 50)["cert_count"] == 50
