"""Unit tests for recallstorm.pricing.pos_sale_blocks."""
from recallstorm.pricing.pos_sale_blocks import (
    PosHardLockRule,
    RegisterBlockInjector,
    audit_pos_lock_coverage_by_store,
    block_manual_department_key_entry,
    compile_pos_stop_sale_xml_payload,
    generate_cashier_halt_screen_text,
    handle_offline_register_resync,
    intercept_weight_embedded_barcodes,
    log_blocked_scan_attempt_events,
    push_emergency_plu_lock_to_lanes,
    test_self_checkout_override_denial as run_sco_override_check,
    verify_lane_sync_heartbeat_status,
)


def test_pos_sale_blocks():
    assert PosHardLockRule().status == "ACTIVE"
    assert RegisterBlockInjector().status == "ACTIVE"
    assert "hardLock=\"true\"" in compile_pos_stop_sale_xml_payload("07502264930572")
    assert push_emergency_plu_lock_to_lanes("WM1", 20)["lanes_updated"] == 20
    assert verify_lane_sync_heartbeat_status(20, 20)["all_synced"] is True
    assert block_manual_department_key_entry("WM1", "D92")["blocked"] is True
    assert intercept_weight_embedded_barcodes("01234")["wildcard_blocked"] is True
    assert run_sco_override_check("S1", True)["override_denied"] is True
    assert log_blocked_scan_attempt_events("WM1", "S1")["resweep_triggered"] is True
    assert handle_offline_register_resync("LANE-02", 3)["applied"] == 3
    assert "STOP SALE" in generate_cashier_halt_screen_text("Rainbow Sprinkles")
    assert audit_pos_lock_coverage_by_store(50, 50)["complete"] is True
