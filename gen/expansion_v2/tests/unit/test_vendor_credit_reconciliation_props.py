"""Property tests for recallstorm.vendor.credit_reconciliation."""
import random
from recallstorm.vendor.credit_reconciliation import reconcile_unit_cost_discrepancies_on_credit


def test_unit_cost_discrepancy_non_negative():
    rng = random.Random(42)
    for _ in range(25):
        po = rng.uniform(1.0, 20.0)
        cr = rng.uniform(1.0, 20.0)
        assert reconcile_unit_cost_discrepancies_on_credit(po, cr, 10) >= 0.0
