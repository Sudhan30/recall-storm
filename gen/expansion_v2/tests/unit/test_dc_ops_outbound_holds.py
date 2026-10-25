"""Unit tests for recallstorm.dc_ops.outbound_holds."""
from recallstorm.dc_ops.outbound_holds import (
    OutboundWaveInterceptor,
    ShippingDockPurge,
    confirm_clean_outbound_seal_application,
    halt_loading_of_contaminated_trailer_door,
    intercept_pallet_at_stretch_wrap_station,
    log_late_truck_departure_delay_reason,
    prevent_bol_print_until_hold_cleared,
    pull_affected_cases_from_store_build_pallet,
    re_cube_shorted_store_delivery_trailer,
    reprint_adjusted_store_shipping_manifest,
    scan_active_pick_waves_for_recalled_lpn,
    scan_staged_shipping_lanes_with_rfid,
)


def test_outbound_holds():
    assert OutboundWaveInterceptor().status == "ACTIVE"
    assert ShippingDockPurge().status == "ACTIVE"
    assert scan_active_pick_waves_for_recalled_lpn([{"wave_id": "W1", "skus": ["S1"]}], "S1") == ["W1"]
    assert intercept_pallet_at_stretch_wrap_station("LPN1")["halted"] is True
    assert pull_affected_cases_from_store_build_pallet("LPN1", 30, 5)["remaining_cases"] == 25
    assert halt_loading_of_contaminated_trailer_door("DC1", 4)["dock_locked"] is True
    assert reprint_adjusted_store_shipping_manifest("MNF1", 5)["cut_cases"] == 5
    assert scan_staged_shipping_lanes_with_rfid("LANE1", 0)["clear"] is True
    assert prevent_bol_print_until_hold_cleared("TR1", 1)["bol_allowed"] is False
    assert log_late_truck_departure_delay_reason("T1", 20)["reason"] == "RECALL_DOCK_PURGE"
    assert re_cube_shorted_store_delivery_trailer(2000.0, 150.0) == 1850.0
    assert confirm_clean_outbound_seal_application("TR1", "SEAL99")["seal_no"] == "SEAL99"
