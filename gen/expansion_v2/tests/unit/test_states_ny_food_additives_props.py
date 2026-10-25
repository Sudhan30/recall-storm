"""Property tests for recallstorm.states.ny_food_additives."""
import random
from recallstorm.states.ny_food_additives import calculate_ny_civil_penalty


def test_ny_penalty_monotonic():
    rng = random.Random(42)
    for _ in range(25):
        n = rng.randint(1, 50)
        assert calculate_ny_civil_penalty(n, repeat=True) > calculate_ny_civil_penalty(n, repeat=False)
