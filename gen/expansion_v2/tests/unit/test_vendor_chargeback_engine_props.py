"""Property tests for recallstorm.vendor.chargeback_engine."""
import random
from recallstorm.vendor.chargeback_engine import deduct_chargeback_from_ap_remittance


def test_ap_remittance_deduction_conservation_props():
    rng = random.Random(42)
    for _ in range(25):
        ap = round(rng.uniform(0.0, 50000.0), 2)
        cb = round(rng.uniform(0.0, 50000.0), 2)
        res = deduct_chargeback_from_ap_remittance(ap, cb)
        assert abs((res["deducted_usd"] + res["unrecovered_usd"]) - cb) <= 0.02
