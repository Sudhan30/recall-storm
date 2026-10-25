"""Property tests for recallstorm.pricing.price_lookup_blocks."""
from recallstorm.pricing.price_lookup_blocks import monitor_scale_firmware_sync_errors


def test_scale_sync_errors_sorted_props():
    ips = ["10.0.0.9", "10.0.0.2", "10.0.0.5"]
    assert monitor_scale_firmware_sync_errors(ips) == sorted(ips)
