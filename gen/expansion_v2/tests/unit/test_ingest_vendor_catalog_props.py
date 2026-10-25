"""Property tests for recallstorm.ingest.vendor_catalog."""
import random
from recallstorm.ingest.vendor_catalog import merge_vendor_catalog


def test_vendor_catalog_merge_props():
    rng = random.Random(42)
    rows = [
        {"sku_id": f"V{i}", "gtin": f"{rng.randint(100000, 999999)}", "case_units": rng.randint(6, 36)}
        for i in range(25)
    ]
    cat = merge_vendor_catalog(rows)
    assert len(cat.skus) == 25
    for s in cat.skus.values():
        assert len(s.gtin) == 14
