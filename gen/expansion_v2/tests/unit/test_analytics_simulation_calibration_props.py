"""Property tests for recallstorm.analytics.simulation_calibration."""
import random
from recallstorm.analytics.simulation_calibration import update_monte_carlo_prior_probabilities


def test_bayesian_posterior_bounds_props():
    rng = random.Random(42)
    for _ in range(25):
        p = rng.uniform(0.01, 0.99)
        l = rng.uniform(0.01, 0.99)
        post = update_monte_carlo_prior_probabilities(p, l)
        assert 0.0 <= post <= 1.0
