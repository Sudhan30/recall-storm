"""Property tests for recallstorm.states.ny_dietary_supplements."""
import random
from recallstorm.states.ny_dietary_supplements import verify_ny_pos_id_prompt


def test_ny_pos_age_gate_threshold():
    rng = random.Random(42)
    for _ in range(30):
        age = rng.randint(10, 65)
        res = verify_ny_pos_id_prompt("SKU1", age)
        assert res["allowed"] == (age >= 18)
