"""Property tests for recallstorm.inventory.destruction_witness."""
import random
from recallstorm.inventory.destruction_witness import weigh_pre_destruction_pallet_gross


def test_pallet_gross_weight_exceeds_tare_props():
    rng = random.Random(42)
    for _ in range(25):
        cases = rng.randint(1, 50)
        w = rng.uniform(5.0, 40.0)
        assert weigh_pre_destruction_pallet_gross(cases, w, 40.0) > 40.0
