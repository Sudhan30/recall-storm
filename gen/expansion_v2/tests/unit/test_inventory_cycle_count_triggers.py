"""Unit tests for recallstorm.inventory.cycle_count_triggers."""
from recallstorm.inventory.cycle_count_triggers import (
    BlindCountVerifier,
    EmergencyCycleCountTask,
    audit_top_stock_riser_locations,
    close_cycle_count_investigation,
    dispatch_zero_confirm_aisle_counts,
    flag_unexpected_found_lot_stock,
    prioritize_high_velocity_store_counts,
    reconcile_display_endcap_secondary_locs,
    require_dual_associate_blind_count,
    track_rf_scanner_count_timestamps,
    validate_case_pack_unit_conversion,
    verify_empty_peg_hook_status,
)


def test_cycle_count_triggers():
    assert EmergencyCycleCountTask().status == "ACTIVE"
    assert BlindCountVerifier().status == "ACTIVE"
    assert dispatch_zero_confirm_aisle_counts("WM1", ["S1", "S2"])["count"] == 2
    assert require_dual_associate_blind_count(12, 12)["matched"] is True
    assert verify_empty_peg_hook_status("A01-1-1-1", 0)["empty_confirmed"] is True
    assert audit_top_stock_riser_locations("WM1", ["A01"])["aisles"] == ["A01"]
    assert reconcile_display_endcap_secondary_locs(10, 5) == 15
    assert flag_unexpected_found_lot_stock("WM1", "S1", 2)["escalate"] is True
    assert prioritize_high_velocity_store_counts({"WM1": 10.0, "WM2": 50.0}) == ["WM2", "WM1"]
    assert track_rf_scanner_count_timestamps("A1", 12.0)["valid_dwell"] is True
    assert validate_case_pack_unit_conversion(2, 3, 12) == 27
    assert close_cycle_count_investigation("TSK1", True)["closed"] is True
