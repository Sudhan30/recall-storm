"""Unit tests for recallstorm.dc_ops.yard_management."""
from recallstorm.dc_ops.yard_management import (
    ReeferHoldMonitor,
    YardTrailerQuarantine,
    apply_digital_glad_hand_lock_in_yms,
    assign_isolated_hazmat_parking_stall,
    audit_daily_yard_check_inventory_sync,
    locate_affected_drop_trailer_in_yard_slot,
    log_security_gate_seal_verification_on_exit,
    manage_detention_clock_on_held_equipment,
    monitor_quarantined_reefer_fuel_and_temp,
    prevent_yard_jockey_move_to_outbound_door,
    prioritize_hot_recall_return_trailer_docking,
    track_3pl_destruction_shuttle_trailers,
)


def test_yard_management():
    assert YardTrailerQuarantine().status == "ACTIVE"
    assert ReeferHoldMonitor().status == "ACTIVE"
    assert locate_affected_drop_trailer_in_yard_slot({"TR1": "SLOT-12"}, "TR1") == "SLOT-12"
    assert apply_digital_glad_hand_lock_in_yms("TR1")["locked"] is True
    assert monitor_quarantined_reefer_fuel_and_temp("TR1", 15.0, 34.0)["refuel_needed"] is True
    assert prioritize_hot_recall_return_trailer_docking(["TR2", "TR1"]) == ["TR1", "TR2"]
    assert track_3pl_destruction_shuttle_trailers("SH1", 200)["cases_loaded"] == 200
    assert prevent_yard_jockey_move_to_outbound_door("TR1", "OUTBOUND")["move_blocked"] is True
    assert log_security_gate_seal_verification_on_exit("TR1", "S1", "G1")["guard_id"] == "G1"
    assert manage_detention_clock_on_held_equipment(58.0, 48.0, 15.0) == 150.0
    assert assign_isolated_hazmat_parking_stall("DC1", "TR1") == "DC1-HAZ-YARD-01"
    assert audit_daily_yard_check_inventory_sync({"TR1", "TR2"}, {"TR1"}) == ["TR2"]
