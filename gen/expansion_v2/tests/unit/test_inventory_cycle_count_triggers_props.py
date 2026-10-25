"""Property tests for recallstorm.inventory.cycle_count_triggers."""
import random
from recallstorm.inventory.cycle_count_triggers import validate_case_pack_unit_conversion


def test_case_pack_conversion_props():
    rng = random.Random(42)
    for _ in range(25):
        c = rng.randint(0, 20)
        e = rng.randint(0, 11)
        tot = validate_case_pack_unit_conversion(c, e, 12)
        assert tot // 12 == c and tot % 12 == e
