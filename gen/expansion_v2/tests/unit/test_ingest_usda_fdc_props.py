"""Property tests for recallstorm.ingest.usda_fdc."""
import random
from recallstorm.ingest.usda_fdc import fdc_to_sku


def test_fdc_to_sku_props():
    rng = random.Random(42)
    for _ in range(25):
        fid = rng.randint(100000, 9999999)
        sku = fdc_to_sku({"fdcId": fid, "gtinUpc": str(fid), "description": "Item", "ingredients": "WATER"})
        assert sku.sku_id == f"FDC{fid}"
        assert len(sku.gtin) == 14
