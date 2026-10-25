"""Unit tests for recallstorm.inventory.cross_dock_allocation."""
from recallstorm.inventory.cross_dock_allocation import (
    CrossDockHoldInterceptor,
    FlowThroughSplitter,
    balance_multi_store_master_cartons,
    break_store_assigned_pallet_ties,
    cancel_outbound_shipping_labels,
    divert_flow_through_to_dc_hold,
    identify_pre_allocated_cross_dock_pallets,
    notify_merchandising_of_cut_allocations,
    recalculation_store_allocation_shorts,
    record_cross_dock_interception_scan,
    release_uncontaminated_sibling_cases,
    update_wms_put_to_store_lights,
)


def test_cross_dock_allocation():
    assert CrossDockHoldInterceptor().status == "ACTIVE"
    assert FlowThroughSplitter().status == "ACTIVE"
    assert identify_pre_allocated_cross_dock_pallets([{"lpn": "L1", "skus": ["S1"]}], "S1") == ["L1"]
    assert break_store_assigned_pallet_ties("L1", "WM1")["unbound_store"] == "WM1"
    assert divert_flow_through_to_dc_hold("L1")["hold_zone"] == "DC-QZONE-01"
    assert recalculation_store_allocation_shorts(20, 5) == 15
    assert update_wms_put_to_store_lights("XD01", "S1")["lights_off"] is True
    assert cancel_outbound_shipping_labels(["LBL2", "LBL1"]) == ["LBL1", "LBL2"]
    assert record_cross_dock_interception_scan("DC1", "L1")["lpn"] == "L1"
    assert balance_multi_store_master_cartons(24, 6) == 4
    assert notify_merchandising_of_cut_allocations("S1", 5)["cut_cases"] == 5
    assert release_uncontaminated_sibling_cases("L1", 10)["clean_cases"] == 10
