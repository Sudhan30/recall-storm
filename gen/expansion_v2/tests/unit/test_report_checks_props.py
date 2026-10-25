"""Property tests for recallstorm.report.checks."""
import random
from recallstorm.report.checks import check_capacity


def test_check_capacity_props():
    rng = random.Random(42)
    for _ in range(25):
        c = rng.uniform(10.0, 5000.0)
        mnf = [
            {
                "type": "route_manifest",
                "manifest_id": "M1",
                "limits": {"cube_ft3": 3400.0, "weight_lb": 40000.0},
                "stops": [{"store_id": "WM1", "cases": 10, "cube_ft3": c, "weight_lb": 100.0}],
            }
        ]
        assert (len(check_capacity(mnf)) == 0) == (c <= 3400.0)
