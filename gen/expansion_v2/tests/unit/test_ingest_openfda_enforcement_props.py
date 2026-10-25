"""Property tests for recallstorm.ingest.openfda_enforcement."""
import random
from recallstorm.ingest.openfda_enforcement import extract_lot_codes, extract_product_gtins


def test_openfda_extract_props():
    rng = random.Random(42)
    for i in range(25):
        lot = f"LOT{rng.randint(1000, 9999)}"
        gtin = f"{rng.randint(10**11, 10**12 - 1):012d}"
        text = f"Product UPC {gtin} with Lot: {lot}"
        assert lot in extract_lot_codes(text)
        assert gtin.zfill(14) in extract_product_gtins(text)
