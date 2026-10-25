"""Property tests for recallstorm.dc_ops.hazmat_segregation."""
import random
from recallstorm.dc_ops.hazmat_segregation import track_acute_hazardous_waste_p_list_limits


def test_p_list_1kg_threshold_props():
    rng = random.Random(42)
    for _ in range(25):
        kg = rng.uniform(0.0, 3.0)
        assert track_acute_hazardous_waste_p_list_limits(kg, 1.0)["lqg_triggered"] == (kg >= 1.0)
