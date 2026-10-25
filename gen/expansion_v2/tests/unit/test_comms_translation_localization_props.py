"""Property tests for recallstorm.comms.translation_localization."""
import random
from recallstorm.comms.translation_localization import check_reading_grade_level_simplicity


def test_reading_grade_simplicity_props():
    rng = random.Random(42)
    for _ in range(25):
        wps = rng.uniform(5.0, 30.0)
        assert check_reading_grade_level_simplicity(wps, 18.0)["plain_language"] == (wps <= 18.0)
