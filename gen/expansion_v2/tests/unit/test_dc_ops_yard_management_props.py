"""Property tests for recallstorm.dc_ops.yard_management."""
import random
from recallstorm.dc_ops.yard_management import monitor_quarantined_reefer_fuel_and_temp


def test_reefer_fuel_threshold_props():
    rng = random.Random(42)
    for _ in range(25):
        pct = rng.uniform(0.0, 100.0)
        assert monitor_quarantined_reefer_fuel_and_temp("TR1", pct)["refuel_needed"] == (pct < 25.0)
