"""Unit tests for recallstorm.food_safety.haccp_deviations."""
from recallstorm.food_safety.haccp_deviations import (
    CcpDeviationEvent,
    CorrectiveActionPlan,
    document_root_cause_disposition,
    evaluate_cooking_lethality_log,
    flag_metal_detector_reject_spike,
    generate_fsis_noncompliance_response,
    link_deviation_to_batch_id,
    lock_affected_production_window,
    require_qa_manager_countersign,
    trigger_haccp_reassessment_hold,
    validate_test_piece_challenge_log,
    verify_cooling_curve_compliance,
)


def test_haccp_deviations():
    assert CcpDeviationEvent().status == "ACTIVE"
    assert CorrectiveActionPlan().status == "ACTIVE"
    assert evaluate_cooking_lethality_log(170.0, 165.0)["achieved"] is True
    assert flag_metal_detector_reject_spike(8, 5)["spike"] is True
    assert verify_cooling_curve_compliance(65.0, 38.0)["compliant"] is True
    assert trigger_haccp_reassessment_hold("B1")["batch_id"] == "B1"
    assert document_root_cause_disposition("B1", "Steam valve drop")["batch_id"] == "B1"
    assert validate_test_piece_challenge_log(1.5, 2.0, 2.5)["passed"] is True
    assert link_deviation_to_batch_id("DEV1", "B1")["batch_id"] == "B1"
    assert len(lock_affected_production_window("L1", "2026-12-30T10:00", "2026-12-30T11:00")["window"]) == 2
    assert require_qa_manager_countersign("DEV1", True)["approved"] is True
    assert generate_fsis_noncompliance_response("NR1", "Fixed")["nr_id"] == "NR1"
