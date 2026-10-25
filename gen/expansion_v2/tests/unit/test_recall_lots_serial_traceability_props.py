"""Property tests for recallstorm.recall_lots.serial_traceability."""
import random
from recallstorm.gs1.gtin import gtin_check_digit
from recallstorm.recall_lots.serial_traceability import match_sscc18_pallet_labels


def test_sscc18_check_digit_props():
    rng = random.Random(42)
    for _ in range(25):
        b17 = f"{rng.randint(0, 10**17 - 1):017d}"
        chk = gtin_check_digit(b17)
        assert match_sscc18_pallet_labels(f"{b17}{chk}")["valid"] is True
