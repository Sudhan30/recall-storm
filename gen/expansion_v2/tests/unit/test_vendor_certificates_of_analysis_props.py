"""Property tests for recallstorm.vendor.certificates_of_analysis."""
import random
from recallstorm.vendor.certificates_of_analysis import check_heavy_metal_pfas_pass_fail_limits


def test_coa_pass_fail_threshold_props():
    rng = random.Random(42)
    for _ in range(25):
        val = rng.uniform(0.0, 100.0)
        assert check_heavy_metal_pfas_pass_fail_limits(val, 50.0)["passed"] == (val <= 50.0)
