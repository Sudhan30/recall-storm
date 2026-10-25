"""Unit tests for recallstorm.governance.training_certification."""
from recallstorm.governance.training_certification import (
    ComplianceLmsTracker,
    RoleCertificationGate,
    assign_mandatory_recall_drill_microlearning,
    audit_new_hire_onboarding_safety_modules,
    block_untrained_associate_from_quarantine_tasks,
    generate_osha_fda_training_inspection_log,
    notify_store_manager_of_lapsed_certifications,
    score_simulated_drill_assessment_quizzes,
    sync_lms_completion_with_labor_skill_matrix,
    track_forklift_hazmat_spill_training_expiry,
    trigger_remedial_training_after_failed_pull,
    verify_annual_fsma_204_handler_certification,
)


def test_training_certification():
    assert ComplianceLmsTracker().status == "ACTIVE"
    assert RoleCertificationGate().status == "ACTIVE"
    assert assign_mandatory_recall_drill_microlearning(["A1", "A2"])["assigned_count"] == 2
    assert verify_annual_fsma_204_handler_certification("A1", 100)["current"] is True
    assert block_untrained_associate_from_quarantine_tasks("A1", False)["blocked"] is True
    assert track_forklift_hazmat_spill_training_expiry([{"associate_id": "A1", "expires": "2025-01-01"}], "2026-12-30") == ["A1"]
    assert score_simulated_drill_assessment_quizzes(9, 10)["passed"] is True
    assert trigger_remedial_training_after_failed_pull("A1", "WM1")["remedial_assigned"] is True
    assert sync_lms_completion_with_labor_skill_matrix("A1", "HAZMAT")["synced"] is True
    assert audit_new_hire_onboarding_safety_modules(20, 19) == 95.0
    assert generate_osha_fda_training_inspection_log("WM1", 15)["certified_count"] == 15
    assert notify_store_manager_of_lapsed_certifications("WM1", ["A1"])["lapsed_count"] == 1
