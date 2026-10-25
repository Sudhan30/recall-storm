"""Property tests for recallstorm.vendor.dsd_coordination."""
import random
from recallstorm.vendor.dsd_coordination import audit_driver_pulled_case_counts_at_exit


def test_driver_count_shortage_props():
    rng = random.Random(42)
    for _ in range(25):
        pulled = rng.randint(5, 50)
        cred = rng.randint(0, pulled)
        res = audit_driver_pulled_case_counts_at_exit(pulled, cred)
        assert res["shortage"] + cred == pulled
