"""Property tests for recallstorm.dc_ops.cold_storage_holds."""
import random
from recallstorm.dc_ops.cold_storage_holds import verify_minus_ten_f_freezer_quarantine_zone


def test_freezer_zone_temp_props():
    rng = random.Random(42)
    for _ in range(25):
        t = rng.uniform(-25.0, 20.0)
        assert verify_minus_ten_f_freezer_quarantine_zone(t, 0.0)["compliant"] == (t <= 0.0)
