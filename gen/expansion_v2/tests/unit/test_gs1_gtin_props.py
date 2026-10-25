"""Property tests for recallstorm.gs1.gtin."""
import random
from recallstorm.gs1.gtin import gtin_check_digit, is_valid_gtin, normalize_gtin


def test_gtin_check_digit_roundtrip_props():
    rng = random.Random(42)
    for _ in range(40):
        body13 = f"{rng.randint(0, 10**13 - 1):013d}"
        chk = gtin_check_digit(body13)
        g14 = f"{body13}{chk}"
        assert is_valid_gtin(g14)
        assert normalize_gtin(g14[2:]) == g14
        # Flipping check digit must invalidate GTIN
        bad_chk = (chk + 1) % 10
        assert not is_valid_gtin(f"{body13}{bad_chk}")
