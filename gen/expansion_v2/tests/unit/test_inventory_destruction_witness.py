"""Unit tests for recallstorm.inventory.destruction_witness."""
from recallstorm.inventory.destruction_witness import (
    CompactorLogTracker,
    WitnessedDestructionRecord,
    archive_epa_rcra_waste_profile,
    audit_unwitnessed_disposal_exceptions,
    capture_compactor_cycle_video_hash,
    generate_dual_signature_affidavit,
    lock_destroyed_lpn_in_wms,
    record_denaturing_chemical_application,
    schedule_regulatory_witness_appointment,
    upload_geotagged_destruction_photos,
    verify_landfill_manifest_ticket_id,
    weigh_pre_destruction_pallet_gross,
)


def test_destruction_witness():
    assert WitnessedDestructionRecord().status == "ACTIVE"
    assert CompactorLogTracker().status == "ACTIVE"
    assert schedule_regulatory_witness_appointment("WM1", "FDA")["agency"] == "FDA"
    assert len(capture_compactor_cycle_video_hash("CLIP1")) == 16
    assert record_denaturing_chemical_application("B1")["denatured"] is True
    assert weigh_pre_destruction_pallet_gross(10, 20.0, 40.0) == 240.0
    assert generate_dual_signature_affidavit("MGR1", "LP1", 100)["units"] == 100
    assert verify_landfill_manifest_ticket_id("TKT1", 2.0)["net_tons"] == 2.0
    assert upload_geotagged_destruction_photos("WM1", 34.0, -118.0)["store_id"] == "WM1"
    assert audit_unwitnessed_disposal_exceptions([{"store_id": "WM1", "witness_id": None}]) == ["WM1"]
    assert lock_destroyed_lpn_in_wms("LPN1")["status"] == "DESTROYED"
    assert archive_epa_rcra_waste_profile("S1")["sku_id"] == "S1"
