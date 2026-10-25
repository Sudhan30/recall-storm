"""Unit tests for recallstorm.governance.approvals_workflow."""
from recallstorm.governance.approvals_workflow import (
    CrisisSignOffRouter,
    MultiStageApprovalGate,
    block_premature_quarantine_bin_unlocking,
    capture_cryptographic_digital_signatures,
    enforce_dual_control_on_chainwide_pulls,
    escalate_unapproved_holds_past_15_mins,
    generate_sox_compliant_approval_trail,
    log_verbal_war_room_authorization_overrides,
    manage_delegation_of_authority_on_weekends,
    route_class_i_pos_lock_for_vp_approval,
    track_approval_turnaround_bottlenecks,
    verify_qa_director_clearance_for_release,
)


def test_approvals_workflow():
    assert MultiStageApprovalGate().status == "ACTIVE"
    assert CrisisSignOffRouter().status == "ACTIVE"
    assert route_class_i_pos_lock_for_vp_approval("R1", "VP1")["vp_id"] == "VP1"
    assert enforce_dual_control_on_chainwide_pulls("QA1", "OPS1")["dual_control_met"] is True
    assert len(capture_cryptographic_digital_signatures("QA1", "PULL", "2026-12-30T18:00")) == 16
    assert escalate_unapproved_holds_past_15_mins(20.0)["escalated"] is True
    assert log_verbal_war_room_authorization_overrides("VP1", "SC1")["ratification_due_hours"] == 4
    assert verify_qa_director_clearance_for_release("H1", True)["release_allowed"] is True
    assert manage_delegation_of_authority_on_weekends("VP1", "DEL1", True) == "DEL1"
    assert block_premature_quarantine_bin_unlocking("B1", False)["unlock_blocked"] is True
    assert track_approval_turnaround_bottlenecks({"QA": 5.0, "LEGAL": 18.0}) == "LEGAL"
    assert generate_sox_compliant_approval_trail([{"id": "A1"}])["sox_compliant"] is True
