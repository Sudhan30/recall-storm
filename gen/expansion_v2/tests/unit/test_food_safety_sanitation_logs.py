"""Unit tests for recallstorm.food_safety.sanitation_logs."""
from recallstorm.food_safety.sanitation_logs import (
    SsopExecutionRecord,
    SwabVerificationTracker,
    audit_third_party_pest_reports,
    flag_overdue_slicer_teardown,
    generate_ssop_remediation_ticket,
    link_sanitation_crew_to_aisle,
    log_food_contact_atp_rlu_scores,
    schedule_listeria_zone_1_swabs,
    track_chemical_dispensing_titration,
    trigger_post_recall_deep_clean,
    validate_drain_sanitation_signoff,
    verify_quaternary_ammonia_ppm,
)


def test_sanitation_logs():
    assert SsopExecutionRecord().status == "ACTIVE"
    assert SwabVerificationTracker().status == "ACTIVE"
    assert schedule_listeria_zone_1_swabs("WM1", ["SLICER1", "TABLE1"])["site_count"] == 2
    assert verify_quaternary_ammonia_ppm(300.0)["in_range"] is True
    assert log_food_contact_atp_rlu_scores("SLICER1", 45, 100)["passed"] is True
    assert trigger_post_recall_deep_clean("WM1", "A01")["aisle"] == "A01"
    assert validate_drain_sanitation_signoff("WM1", "A1")["signed_by"] == "A1"
    assert track_chemical_dispensing_titration("ST1", 250.0)["ppm"] == 250.0
    assert flag_overdue_slicer_teardown("SL1", 5.5)["overdue"] is True
    assert link_sanitation_crew_to_aisle("A1", "A01")["associate_id"] == "A1"
    assert audit_third_party_pest_reports("WM1", 0)["clean"] is True
    assert generate_ssop_remediation_ticket("WM1", "SLICER1")["surface_id"] == "SLICER1"
