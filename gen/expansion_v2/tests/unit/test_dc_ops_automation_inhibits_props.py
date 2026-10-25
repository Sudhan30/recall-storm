"""Property tests for recallstorm.dc_ops.automation_inhibits."""
from recallstorm.dc_ops.automation_inhibits import sync_wcs_warehouse_control_with_wms_hold


def test_wcs_wms_sync_props():
    s = {f"LPN{i}" for i in range(10)}
    assert sync_wcs_warehouse_control_with_wms_hold(s, s)["in_sync"] is True
    assert sync_wcs_warehouse_control_with_wms_hold(s, set())["in_sync"] is False
