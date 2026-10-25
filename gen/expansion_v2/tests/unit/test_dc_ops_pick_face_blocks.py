"""Unit tests for recallstorm.dc_ops.pick_face_blocks."""
from recallstorm.dc_ops.pick_face_blocks import (
    ActivePickSlotHold,
    ReplenishmentStopper,
    audit_partial_case_pick_remnants,
    block_automated_crane_asrs_retrieval,
    cancel_pending_letdown_replenishment_tasks,
    freeze_primary_forward_pick_location,
    lock_case_flow_rack_lane_gravity_feed,
    re_slot_substitute_sku_into_pick_face,
    redirect_voice_pick_operator_around_slot,
    restore_pick_face_after_sanitation,
    trigger_immediate_slot_purge_to_cage,
    verify_empty_pick_slot_via_barcode_scan,
)


def test_pick_face_blocks():
    assert ActivePickSlotHold().status == "ACTIVE"
    assert ReplenishmentStopper().status == "ACTIVE"
    assert freeze_primary_forward_pick_location("DC1", "S-101")["frozen"] is True
    assert cancel_pending_letdown_replenishment_tasks(["T2", "T1"]) == ["T1", "T2"]
    assert redirect_voice_pick_operator_around_slot("S-101", "S-102")["sub_slot"] == "S-102"
    assert trigger_immediate_slot_purge_to_cage("DC1", "S-101", 20)["cases"] == 20
    assert lock_case_flow_rack_lane_gravity_feed("FL-1")["locked"] is True
    assert verify_empty_pick_slot_via_barcode_scan("S-101", "99")["verified_empty"] is True
    assert re_slot_substitute_sku_into_pick_face("S-101", "SUB1")["sub_sku_id"] == "SUB1"
    assert block_automated_crane_asrs_retrieval("CR1", "LPN1")["blocked"] is True
    assert audit_partial_case_pick_remnants("S-101", 4)["loose_eaches"] == 4
    assert restore_pick_face_after_sanitation("S-101", True)["active"] is True
