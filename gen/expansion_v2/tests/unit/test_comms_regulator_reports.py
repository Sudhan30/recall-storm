"""Unit tests for recallstorm.comms.regulator_reports."""
from recallstorm.comms.regulator_reports import (
    InspectorVisitPacket,
    RegulatoryStatusFiling,
    archive_final_recall_closure_letter,
    compile_fda_district_recall_status_report,
    format_state_dept_of_ag_store_list,
    log_regulatory_in_store_sample_receipts,
    manage_regulatory_inquiry_response_sla,
    prepare_store_manager_inspector_binder,
    redact_pii_from_submission_packages,
    track_fda_form_482_483_uploads,
    validate_report_against_agency_schema,
    verify_zero_stock_attestation_accuracy,
)


def test_regulator_reports():
    assert RegulatoryStatusFiling().status == "ACTIVE"
    assert InspectorVisitPacket().status == "ACTIVE"
    rep = compile_fda_district_recall_status_report("R1", 45, 50)
    assert rep["pct"] == 90.0
    assert format_state_dept_of_ag_store_list("CA", ["WM1"])["state"] == "CA"
    assert prepare_store_manager_inspector_binder("WM1", 12)["pull_count"] == 12
    assert log_regulatory_in_store_sample_receipts("WM1", "484-1")["duplicate_retained"] is True
    assert track_fda_form_482_483_uploads("WM1", "FDA_482")["form_type"] == "FDA_482"
    assert verify_zero_stock_attestation_accuracy(True, 0)["accurate"] is True
    assert "[REDACTED_EMAIL]" in redact_pii_from_submission_packages("Email bob@example.com")
    assert validate_report_against_agency_schema({"recall_id": "R1"})["valid"] is True
    assert manage_regulatory_inquiry_response_sla(10.0, 24.0)["within_sla"] is True
    assert archive_final_recall_closure_letter("R1", "2027-03-01")["terminated_on"] == "2027-03-01"
