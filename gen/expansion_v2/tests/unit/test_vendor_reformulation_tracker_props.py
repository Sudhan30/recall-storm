"""Property tests for recallstorm.vendor.reformulation_tracker."""
import random
from recallstorm.vendor.reformulation_tracker import report_category_compliance_readiness_pct


def test_readiness_pct_bounds():
    rng = random.Random(42)
    for _ in range(25):
        tot = rng.randint(1, 100)
        ok = rng.randint(0, tot)
        pct = report_category_compliance_readiness_pct(ok, tot)
        assert 0.0 <= pct <= 100.0
