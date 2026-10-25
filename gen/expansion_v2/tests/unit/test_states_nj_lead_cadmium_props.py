"""Property tests for recallstorm.states.nj_lead_cadmium."""
import random
from recallstorm.states.nj_lead_cadmium import calculate_nj_daily_intake_exposure


def test_nj_daily_intake_bilinear_props():
    rng = random.Random(42)
    for _ in range(25):
        g = rng.uniform(1.0, 50.0)
        ppb = rng.uniform(10.0, 500.0)
        assert calculate_nj_daily_intake_exposure(g, ppb) >= 0.0
