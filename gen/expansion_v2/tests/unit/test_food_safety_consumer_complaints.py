"""Unit tests for recallstorm.food_safety.consumer_complaints."""
from recallstorm.food_safety.consumer_complaints import (
    ClusterSignalDetector,
    IllnessComplaintTicket,
    calculate_incubation_period_match,
    check_foreign_material_photo_hash,
    cross_reference_iwaspoisoned_feed,
    detect_geographic_complaint_cluster,
    escalate_hospitalization_report,
    generate_fda_medwatch_draft,
    ingest_call_center_symptom_log,
    link_loyalty_card_purchase_lot,
    track_sample_retrieval_courier,
    trigger_precautionary_lot_hold,
)


def test_consumer_complaints():
    assert IllnessComplaintTicket().status == "ACTIVE"
    assert ClusterSignalDetector().status == "ACTIVE"
    assert ingest_call_center_symptom_log("T1", ["nausea", "fever"])["ticket_id"] == "T1"
    assert calculate_incubation_period_match(24.0, "SALMONELLA")["matched"] is True
    assert detect_geographic_complaint_cluster({"WM1": 4, "WM2": 1}, 3) == ["WM1"]
    assert link_loyalty_card_purchase_lot("LOY1", "S1", "L1")["lot_id"] == "L1"
    assert escalate_hospitalization_report("T1", True)["priority"] == "CRITICAL"
    assert len(check_foreign_material_photo_hash("img_data")) == 16
    assert cross_reference_iwaspoisoned_feed("WM1", 3)["alert"] is True
    assert trigger_precautionary_lot_hold("S1", "L1")["status"] == "HOLD_VERIFY"
    assert generate_fda_medwatch_draft("T1", "S1")["sku_id"] == "S1"
    assert track_sample_retrieval_courier("T1", "TRK1")["tracking_no"] == "TRK1"
