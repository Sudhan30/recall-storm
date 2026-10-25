"""Unit tests for recallstorm.vendor.supplier_scorecards."""
from recallstorm.vendor.supplier_scorecards import (
    RecallPenaltyWeighting,
    VendorComplianceScorecard,
    benchmark_dsd_vs_warehouse_compliance,
    calculate_recall_frequency_severity_index,
    evaluate_chargeback_dispute_friction_rate,
    export_executive_vendor_risk_matrix,
    feed_scorecard_to_merchandising_line_review,
    penalize_late_recall_notification_lag,
    rank_category_suppliers_by_safety_risk,
    score_lot_traceability_data_completeness,
    track_reformulation_deadline_adherence,
    trigger_probationary_business_review,
)


def test_supplier_scorecards():
    assert VendorComplianceScorecard().status == "ACTIVE"
    assert RecallPenaltyWeighting().status == "ACTIVE"
    assert calculate_recall_frequency_severity_index(1, 2, 1) == 19.0
    assert penalize_late_recall_notification_lag(4.0, 2.0) == 10.0
    assert score_lot_traceability_data_completeness(9, 10) == 90.0
    assert evaluate_chargeback_dispute_friction_rate(2, 10) == 0.2
    assert rank_category_suppliers_by_safety_risk({"V1": 10.0, "V2": 25.0}) == ["V2", "V1"]
    assert trigger_probationary_business_review("V1", 60.0)["probation"] is True
    assert feed_scorecard_to_merchandising_line_review("V1", 88.0)["score"] == 88.0
    assert benchmark_dsd_vs_warehouse_compliance(90.0, 95.0)["delta"] == -5.0
    assert track_reformulation_deadline_adherence(5, 5) == 100.0
    assert export_executive_vendor_risk_matrix([{"vendor_id": "V1"}])["vendor_count"] == 1
