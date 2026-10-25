"""Property tests for recallstorm.gs1.digital_link."""
import random
from recallstorm.gs1.digital_link import build_digital_link, canonical_digital_link, parse_digital_link


def test_digital_link_canonical_idempotence():
    rng = random.Random(42)
    for _ in range(25):
        lot = f"LOT{rng.randint(100, 999)}"
        uri = build_digital_link("00073621007017", lot=lot, expiry="270510")
        assert canonical_digital_link(uri) == uri
        assert parse_digital_link(uri)["10"] == lot
