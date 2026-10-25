"""Unit tests for recallstorm.vendor.indemnification_claims."""
from recallstorm.vendor.indemnification_claims import (
    InsuranceTenderTracker,
    LegalIndemnityClaim,
    archive_executed_settlement_releases,
    calculate_total_incident_tort_exposure,
    check_additional_insured_endorsement_status,
    coordinate_outside_counsel_litigation_hold,
    flag_lapsed_supplier_insurance_policies,
    link_master_supply_agreement_indemnity_clause,
    manage_subrogation_recovery_workflows,
    tender_consumer_injury_claim_to_vendor,
    track_defense_cost_reimbursement_ledger,
    verify_vendor_product_liability_coi_limits,
)


def test_indemnification_claims():
    assert LegalIndemnityClaim().status == "ACTIVE"
    assert InsuranceTenderTracker().status == "ACTIVE"
    assert verify_vendor_product_liability_coi_limits(10.0, 5.0)["sufficient"] is True
    assert check_additional_insured_endorsement_status("V1", True)["compliant"] is True
    assert tender_consumer_injury_claim_to_vendor("CLM1", "V1")["tendered"] is True
    assert track_defense_cost_reimbursement_ledger("CLM1", 12500.0)["legal_fees_usd"] == 12500.0
    assert link_master_supply_agreement_indemnity_clause("V1")["clause"] == "Sec. 14.2"
    assert flag_lapsed_supplier_insurance_policies([{"vendor_id": "V1", "expires": "2025-01-01"}], "2026-12-30") == ["V1"]
    assert calculate_total_incident_tort_exposure(4, 25000.0) == 100000.0
    assert coordinate_outside_counsel_litigation_hold("R1", ["a@example.com"])["custodians"] == 1
    assert manage_subrogation_recovery_workflows("CLM1", "INS1")["insurer_id"] == "INS1"
    assert archive_executed_settlement_releases("CLM1", "h1")["claim_id"] == "CLM1"
