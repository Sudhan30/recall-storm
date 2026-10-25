"""Property tests for recallstorm.gs1.epcis."""
import random
from recallstorm.gs1.epcis import epc_to_gtin
from recallstorm.gs1.gtin import is_valid_gtin


def test_epc_to_gtin_always_valid_gtin14():
    rng = random.Random(42)
    for _ in range(25):
        comp = f"{rng.randint(100000, 999999):06d}"
        item = f"0{rng.randint(100000, 999999):06d}"
        urn = f"urn:epc:id:sgtin:{comp}.{item}.123"
        g14 = epc_to_gtin(urn)
        assert len(g14) == 14 and is_valid_gtin(g14)
