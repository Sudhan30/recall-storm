"""Unit tests for recallstorm.pricing.price_file_governance."""
from recallstorm.pricing.price_file_governance import (
    EmergencyPriceFilePush,
    PosSyncAuditor,
    archive_point_in_time_pos_table,
    compare_host_vs_lane_item_record,
    escalate_stalled_store_pos_controllers,
    log_price_file_override_authorizations,
    monitor_store_controller_apply_status,
    quarantine_corrupt_plu_delta_files,
    sign_cryptographic_price_file_hash,
    trigger_fallback_dialup_price_push,
    validate_emergency_item_maintenance_batch,
    verify_multi_banner_price_zone_scope,
)


def test_price_file_governance():
    assert EmergencyPriceFilePush().status == "ACTIVE"
    assert PosSyncAuditor().status == "ACTIVE"
    assert validate_emergency_item_maintenance_batch("B1", 10)["valid"] is True
    assert len(sign_cryptographic_price_file_hash("payload")) == 16
    assert monitor_store_controller_apply_status("WM1", True)["applied"] is True
    assert trigger_fallback_dialup_price_push("WM1")["channel"] == "LTE_FALLBACK"
    assert compare_host_vs_lane_item_record(True, True)["in_sync"] is True
    assert quarantine_corrupt_plu_delta_files("F1")["quarantined"] is True
    assert escalate_stalled_store_pos_controllers(["WM2", "WM1"]) == ["WM1", "WM2"]
    assert log_price_file_override_authorizations("VP1", "B1")["authorizer_id"] == "VP1"
    assert verify_multi_banner_price_zone_scope(["WALMART", "SAMS"])["banners"] == ["SAMS", "WALMART"]
    assert archive_point_in_time_pos_table("SNAP1", 50)["record_count"] == 50
