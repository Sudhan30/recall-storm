"""Unit tests for recallstorm.vendor.certificates_of_analysis."""
from recallstorm.vendor.certificates_of_analysis import (
    CoaRepository,
    LabResultValidator,
    alert_qa_to_marginal_spec_results,
    archive_regulatory_audit_coa_bundle,
    block_receiving_on_missing_coa_gate,
    check_heavy_metal_pfas_pass_fail_limits,
    detect_altered_fraudulent_coa_pdfs,
    flag_expired_annual_testing_certificates,
    ingest_pdf_edifact_coa_documents,
    link_coa_to_gs1_epcis_lot_master,
    match_coa_batch_id_to_asn_lot,
    verify_iso_17025_lab_accreditation_scope,
)


def test_certificates_of_analysis():
    assert CoaRepository().status == "ACTIVE"
    assert LabResultValidator().status == "ACTIVE"
    assert ingest_pdf_edifact_coa_documents("COA1", "L1")["batch_id"] == "L1"
    assert verify_iso_17025_lab_accreditation_scope("LAB1", True)["valid"] is True
    assert match_coa_batch_id_to_asn_lot(["L1", "L2"], "L1") is True
    assert check_heavy_metal_pfas_pass_fail_limits(15.0, 50.0)["passed"] is True
    assert flag_expired_annual_testing_certificates("2024-05-01", "2026-01-01")["expired"] is True
    assert detect_altered_fraudulent_coa_pdfs("h1", "h2")["fraud_detected"] is True
    assert block_receiving_on_missing_coa_gate("PO1", False)["blocked"] is True
    assert alert_qa_to_marginal_spec_results(48.0, 50.0)["marginal_alert"] is True
    assert link_coa_to_gs1_epcis_lot_master("COA1", "07502264930572", "L1")["lot_id"] == "L1"
    assert archive_regulatory_audit_coa_bundle("R1", ["COA1"])["count"] == 1
