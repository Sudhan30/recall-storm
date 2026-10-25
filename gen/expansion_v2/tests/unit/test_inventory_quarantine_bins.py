"""Unit tests for recallstorm.inventory.quarantine_bins."""
from recallstorm.inventory.quarantine_bins import (
    DigitalHoldLocation,
    QuarantineCageManager,
    assign_locked_backroom_cage_bin,
    audit_aged_quarantine_dwell_time,
    consolidate_partial_hold_cases,
    enforce_wms_directed_putaway_block,
    generate_red_hold_pallet_license_plate,
    log_authorized_quarantine_access,
    prevent_pick_from_quarantine_loc,
    release_cleared_bin_to_active,
    track_quarantine_bin_capacity_cube,
    verify_physical_padlock_seal_number,
)


def test_quarantine_bins():
    assert QuarantineCageManager().status == "ACTIVE"
    assert DigitalHoldLocation().status == "ACTIVE"
    assert assign_locked_backroom_cage_bin("WM1", False) == "WM1-QCAGE-01"
    assert generate_red_hold_pallet_license_plate("DC1", 1) == "RED-LPN-DC1-00001"
    assert enforce_wms_directed_putaway_block("LPN1")["blocked"] is True
    assert verify_physical_padlock_seal_number("C1", "SEAL99")["seal_no"] == "SEAL99"
    assert track_quarantine_bin_capacity_cube(50.0, 200.0)["remaining_ft3"] == 150.0
    assert prevent_pick_from_quarantine_loc("QCAGE-01")["pick_inhibited"] is True
    assert log_authorized_quarantine_access("MGR1", "C1")["associate_id"] == "MGR1"
    assert audit_aged_quarantine_dwell_time(20, 14)["overdue"] is True
    assert consolidate_partial_hold_cases(27, 12) == (2, 3)
    assert release_cleared_bin_to_active("C1", "QA-OK")["released"] is True
