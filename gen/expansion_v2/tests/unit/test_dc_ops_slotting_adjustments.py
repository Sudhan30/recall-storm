"""Unit tests for recallstorm.dc_ops.slotting_adjustments."""
from recallstorm.dc_ops.slotting_adjustments import (
    QuarantineSlottingPlanner,
    SurgeCapacityAllocator,
    balance_freezer_vs_ambient_hold_capacity,
    calculate_cubic_feet_needed_for_recall_hold,
    convert_bulk_floor_stack_to_quarantine_zone,
    isolate_allergen_or_chemical_leaker_racks,
    optimize_forklift_travel_to_compactor_bay,
    re_slot_seasonal_aisle_for_return_staging,
    reserve_dock_doors_for_reverse_consolidation,
    restore_baseline_slotting_post_disposition,
    track_temporary_rack_reconfiguration_cost,
    update_wms_zone_velocity_restrictions,
)


def test_slotting_adjustments():
    assert QuarantineSlottingPlanner().status == "ACTIVE"
    assert SurgeCapacityAllocator().status == "ACTIVE"
    assert calculate_cubic_feet_needed_for_recall_hold(100, 2.0, 1.25) == 250.0
    assert convert_bulk_floor_stack_to_quarantine_zone("DC1", ["B2", "B1"])["bays"] == ["B1", "B2"]
    assert re_slot_seasonal_aisle_for_return_staging("DC1", "S01")["aisle"] == "S01"
    assert isolate_allergen_or_chemical_leaker_racks("R1")["floor_level_only"] is True
    assert optimize_forklift_travel_to_compactor_bay({"B1": 120.0, "B2": 45.0}) == "B2"
    assert reserve_dock_doors_for_reverse_consolidation("DC1", [10, 8])["doors"] == [8, 10]
    assert balance_freezer_vs_ambient_hold_capacity(60, 100, 50)["reefer_trailer_needed"] is True
    assert update_wms_zone_velocity_restrictions("Z1")["velocity_code"] == "HOLD"
    assert track_temporary_rack_reconfiguration_cost(10.0, 35.0) == 350.0
    assert restore_baseline_slotting_post_disposition("DC1", "Z1")["restored"] is True
