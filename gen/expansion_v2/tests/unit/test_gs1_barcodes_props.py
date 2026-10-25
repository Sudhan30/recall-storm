"""Property tests for recallstorm.gs1.barcodes."""
import random
from recallstorm.gs1.barcodes import is_variable_measure, strip_price_embedded, validate_scan


def test_strip_price_embedded_always_valid_gtin():
    rng = random.Random(42)
    for _ in range(25):
        item5 = f"{rng.randint(0, 99999):05d}"
        price5 = f"{rng.randint(100, 99999):05d}"
        raw12 = f"2{item5}{price5}0"
        assert is_variable_measure(raw12)
        stripped = strip_price_embedded(raw12)
        assert validate_scan(stripped)
