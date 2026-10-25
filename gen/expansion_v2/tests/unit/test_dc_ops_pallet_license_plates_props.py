"""Property tests for recallstorm.dc_ops.pallet_license_plates."""
from recallstorm.dc_ops.pallet_license_plates import audit_quarantine_zone_lpn_physical_count


def test_quarantine_lpn_audit_set_difference_props():
    wms = {f"LPN{i}" for i in range(15)}
    scanned = {f"LPN{i}" for i in range(10)}
    res = audit_quarantine_zone_lpn_physical_count(wms, scanned)
    assert len(res["missing_lpns"]) == 5 and res["reconciled"] is False
