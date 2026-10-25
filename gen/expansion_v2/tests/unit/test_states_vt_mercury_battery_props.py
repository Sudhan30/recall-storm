"""Property tests for recallstorm.states.vt_mercury_battery."""
import random
from recallstorm.states.vt_mercury_battery import check_vt_alkaline_mercury_ppm


def test_vt_mercury_zero_tolerance_props():
    rng = random.Random(42)
    for _ in range(25):
        ppm = rng.uniform(0.01, 50.0)
        assert check_vt_alkaline_mercury_ppm(ppm, 0.0)["prohibited"] is True
    assert check_vt_alkaline_mercury_ppm(0.0, 0.0)["prohibited"] is False
