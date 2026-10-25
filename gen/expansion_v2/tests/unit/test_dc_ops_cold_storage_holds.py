"""Unit tests for recallstorm.dc_ops.cold_storage_holds."""
from recallstorm.dc_ops.cold_storage_holds import (
    ColdRoomSegregation,
    FreezerBlastHold,
    allocate_insulated_pallet_covers_for_returns,
    audit_multi_temp_trailer_bulkhead_position,
    log_cold_suit_labor_rotation_limits,
    monitor_ammonia_leak_exposure_in_cold_room,
    prevent_blast_cell_cross_airflow_risk,
    release_tempered_product_with_qa_signoff,
    schedule_defrost_window_for_held_coils,
    track_ice_cream_shrink_from_dock_staging,
    validate_frozen_destruction_rendering_chain,
    verify_minus_ten_f_freezer_quarantine_zone,
)


def test_cold_storage_holds():
    assert FreezerBlastHold().status == "ACTIVE"
    assert ColdRoomSegregation().status == "ACTIVE"
    assert verify_minus_ten_f_freezer_quarantine_zone(-12.0, 0.0)["compliant"] is True
    assert monitor_ammonia_leak_exposure_in_cold_room(30.0, 25.0)["quarantine_room"] is True
    assert track_ice_cream_shrink_from_dock_staging(25.0, 20.0)["melted_risk"] is True
    assert allocate_insulated_pallet_covers_for_returns(8) == 8
    assert prevent_blast_cell_cross_airflow_risk("C1", True)["overwrap_required"] is True
    assert schedule_defrost_window_for_held_coils("RM1", 3)["hour"] == 3
    assert log_cold_suit_labor_rotation_limits(50.0, 45.0)["warmup_break_due"] is True
    assert validate_frozen_destruction_rendering_chain("RND1", True)["approved"] is True
    assert audit_multi_temp_trailer_bulkhead_position("TR1", True)["compliant"] is True
    assert release_tempered_product_with_qa_signoff("LPN1", "QA1")["qa_id"] == "QA1"
