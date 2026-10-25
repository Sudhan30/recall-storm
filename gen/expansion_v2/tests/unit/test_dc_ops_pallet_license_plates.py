"""Unit tests for recallstorm.dc_ops.pallet_license_plates."""
from recallstorm.dc_ops.pallet_license_plates import (
    LpnGenealogyTracker,
    MixedPalletSplitter,
    audit_quarantine_zone_lpn_physical_count,
    block_lpn_consolidation_across_hold_codes,
    flag_ghost_lpns_in_lost_and_found_zone,
    generate_split_pallet_rework_work_order,
    identify_rainbow_pallets_with_recalled_layers,
    invalidate_consumed_or_destroyed_lpns,
    print_replacement_hold_lpn_thermal_labels,
    elace_check := verify_gs1_128_sscc_check_digit_integrity,
    track_lpn_location_move_history_in_wms,
    trace_parent_receiving_lpn_to_child_picks,
)
from recallstorm.gs1.gtin import gtin_check_digit


def test_pallet_license_plates():
    assert LpnGenealogyTracker().status == "ACTIVE"
    assert MixedPalletSplitter().status == "ACTIVE"
    assert trace_parent_receiving_lpn_to_child_picks("P1", {"P1": ["C2", "C1"]}) == ["C1", "C2"]
    assert identify_rainbow_pallets_with_recalled_layers([{"lpn": "L1", "lots": ["A", "B"]}], "A") == ["L1"]
    assert generate_split_pallet_rework_work_order("LPN1", 10)["child_hold_lpn"] == "LPN1-HOLD"
    assert invalidate_consumed_or_destroyed_lpns(["L2", "L1"]) == ["L1", "L2"]
    assert block_lpn_consolidation_across_hold_codes("ACTIVE", "HOLD")["consolidation_allowed"] is False
    b17 = "00073621000000002"
    assert elace_check(f"{b17}{gtin_check_digit(b17)}") is True
    assert len(track_lpn_location_move_history_in_wms("L1", ["RCV", "QZONE"])["moves"]) == 2
    assert flag_ghost_lpns_in_lost_and_found_zone(["G1"]) == ["G1"]
    assert print_replacement_hold_lpn_thermal_labels("L1", 2)["copies"] == 2
    assert audit_quarantine_zone_lpn_physical_count({"L1"}, {"L1"})["reconciled"] is True
