"""Property tests for recallstorm.recall_lots.catch_weight_lots."""
import random
from recallstorm.recall_lots.catch_weight_lots import validate_tare_weight_deductions


def test_tare_weight_deduction_props():
    rng = random.Random(42)
    for _ in range(25):
        gross = rng.uniform(1.0, 20.0)
        tare = rng.uniform(0.01, 0.5)
        net = validate_tare_weight_deductions(gross, tare)
        assert abs((net + tare) - gross) < 1e-2
