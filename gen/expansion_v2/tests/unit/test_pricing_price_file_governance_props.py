"""Property tests for recallstorm.pricing.price_file_governance."""
from recallstorm.pricing.price_file_governance import sign_cryptographic_price_file_hash


def test_price_file_hash_determinism():
    for i in range(15):
        h1 = sign_cryptographic_price_file_hash(f"batch_{i}")
        h2 = sign_cryptographic_price_file_hash(f"batch_{i}")
        assert h1 == h2 and len(h1) == 16
