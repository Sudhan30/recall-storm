"""Property tests for recallstorm.gs1.ai."""
import random
from recallstorm.gs1.ai import build_element_string, parse_element_string


def test_element_string_roundtrip_props():
    rng = random.Random(42)
    for i in range(25):
        lot = f"L{rng.randint(100, 999)}"
        ais = {"01": "00073621007017", "17": "270615", "10": lot, "21": f"S{i}"}
        s = build_element_string(ais)
        assert parse_element_string(s) == ais
