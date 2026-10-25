"""Property tests for recallstorm.food_safety.salvage_reconditioning."""
import random
from recallstorm.food_safety.salvage_reconditioning import segregate_non_salvageable_leakers


def test_segregate_leakers_conservation_props():
    rng = random.Random(42)
    for _ in range(25):
        tot = rng.randint(10, 100)
        leak = rng.randint(0, tot)
        res = segregate_non_salvageable_leakers(tot, leak)
        assert res["intact_cases"] + res["leaker_cases"] == tot
