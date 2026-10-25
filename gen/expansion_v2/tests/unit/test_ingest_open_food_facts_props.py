"""Property tests for recallstorm.ingest.open_food_facts."""
import random
from recallstorm.ingest.open_food_facts import off_to_sku


def test_off_to_sku_props():
    rng = random.Random(42)
    for _ in range(25):
        code = str(rng.randint(10**11, 10**13 - 1))
        sku = off_to_sku({"code": code, "product_name": "Item", "additives_tags": ["en:e127"]})
        assert len(sku.gtin) == 14
        assert "E127" in sku.ingredients
