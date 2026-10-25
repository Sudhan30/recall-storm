"""Property tests for recallstorm.gs1.match."""
from contract import Sku
from recallstorm.gs1.match import match_by_gtin


def test_match_by_gtin_exactness():
    skus = [
        Sku(f"S{i}", f"000736210070{i:02d}", f"Item {i}", "B", "c", "I", True, False, 12, 1.0, 5.0)
        for i in range(10, 30)
    ]
    for s in skus:
        assert match_by_gtin(s.gtin, skus) == [s]
