"""Property tests for recallstorm.recall_lots.fsis_notice_parser."""
import random
from recallstorm.recall_lots.fsis_notice_parser import parse_fsis_poultry_serial_range


def test_poultry_serial_range_count_props():
    rng = random.Random(42)
    for _ in range(25):
        s = rng.randint(1, 500)
        k = rng.randint(0, 20)
        res = parse_fsis_poultry_serial_range(s, s + k)
        assert len(res) == k + 1
