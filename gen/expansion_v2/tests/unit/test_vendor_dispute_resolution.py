"""Unit tests for recallstorm.vendor.dispute_resolution."""
from recallstorm.vendor.dispute_resolution import (
    ChargebackDisputeQueue,
    EvidenceArbitrator,
    apply_partial_settlement_credit_adjustment,
    attach_timestamped_store_pull_scan_logs,
    evaluate_force_majeure_contract_claims,
    generate_arbitration_evidence_dossier,
    ingest_vendor_dispute_portal_submission,
    lock_settled_claims_from_re_submission,
    recalculate_disputed_unit_cost_basis,
    route_high_dollar_dispute_to_merch_vp,
    track_dispute_resolution_cycle_time_days,
    verify_photo_proof_of_affected_lot_code,
)


def test_dispute_resolution():
    assert ChargebackDisputeQueue().status == "ACTIVE"
    assert EvidenceArbitrator().status == "ACTIVE"
    assert ingest_vendor_dispute_portal_submission("D1", "V1", 5000.0)["disputed_usd"] == 5000.0
    assert attach_timestamped_store_pull_scan_logs("D1", 40)["scan_events"] == 40
    assert verify_photo_proof_of_affected_lot_code("D1", True)["verified"] is True
    assert recalculate_disputed_unit_cost_basis(100, 3.25) == 325.0
    assert evaluate_force_majeure_contract_claims("Supply delay")["excused"] is False
    assert route_high_dollar_dispute_to_merch_vp("D1", 30000.0, 25000.0)["vp_routed"] is True
    assert apply_partial_settlement_credit_adjustment(5000.0, 1000.0) == 4000.0
    assert track_dispute_resolution_cycle_time_days(15, 30)["within_sla"] is True
    assert lock_settled_claims_from_re_submission("D1")["locked"] is True
    assert generate_arbitration_evidence_dossier("D1", ["scan.csv", "photo.jpg"])["artifact_count"] == 2
