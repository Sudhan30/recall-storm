"""Property tests for recallstorm.governance.store_sign_offs."""
import random
from recallstorm.governance.store_sign_offs import validate_100_percent_aisle_task_completion


def test_task_completion_signoff_gate_props():
    rng = random.Random(42)
    for _ in range(25):
        tot = rng.randint(1, 50)
        done = rng.randint(0, tot)
        res = validate_100_percent_aisle_task_completion(done, tot)
        assert res["can_sign_off"] == (done == tot)
