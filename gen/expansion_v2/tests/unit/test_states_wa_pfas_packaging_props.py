"""Property tests for recallstorm.states.wa_pfas_packaging."""
import random
from recallstorm.states.wa_pfas_packaging import test_wa_fluorine_ppm_limit as run_fluorine_check


def test_wa_fluorine_threshold_props():
    rng = random.Random(42)
    for _ in range(25):
        ppm = rng.uniform(0.0, 300.0)
        assert run_fluorine_check(ppm, 100.0)["prohibited"] == (ppm >= 100.0)
