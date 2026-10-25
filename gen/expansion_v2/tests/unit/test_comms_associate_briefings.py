"""Unit tests for recallstorm.comms.associate_briefings."""
from recallstorm.comms.associate_briefings import (
    AssociateBriefingTracker,
    ShiftHuddleScript,
    build_deli_bakery_prep_safety_brief,
    customize_script_for_front_end_cashiers,
    export_training_compliance_log,
    generate_five_minute_huddle_talking_points,
    highlight_gloves_ppe_handling_rules,
    provide_customer_de_escalation_phrases,
    quiz_associate_on_lot_code_location,
    record_huddle_attendance_badge_scans,
    track_unbriefed_scheduled_associates,
    update_breakroom_digital_signage_feed,
)


def test_associate_briefings():
    assert ShiftHuddleScript().status == "ACTIVE"
    assert AssociateBriefingTracker().status == "ACTIVE"
    assert len(generate_five_minute_huddle_talking_points("R1", ["Sprinkles"])) == 3
    assert "quarantine" in customize_script_for_front_end_cashiers("R1")
    assert build_deli_bakery_prep_safety_brief("bakery", "RED3")["dept"] == "BAKERY"
    assert quiz_associate_on_lot_code_location("BACK_PANEL", "back_panel")["passed"] is True
    assert record_huddle_attendance_badge_scans("WM1", ["A1", "A2"])["count"] == 2
    assert len(provide_customer_de_escalation_phrases("en")) == 2
    assert "GOGGLES" in highlight_gloves_ppe_handling_rules("caustic cleaner")["ppe"]
    assert update_breakroom_digital_signage_feed("WM1", "SL1")["slide_id"] == "SL1"
    assert track_unbriefed_scheduled_associates(["A1", "A2"], {"A1"}) == ["A2"]
    assert export_training_compliance_log("WM1", 10)["briefed_count"] == 10
