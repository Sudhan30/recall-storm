"""Property tests for recallstorm.dc_ops.receiving_holds."""
import random
from recallstorm.dc_ops.receiving_holds import segregate_mixed_lot_vendor_ti_hi_pallets


def test_segregate_ti_hi_conservation_props():
    rng = random.Random(42)
    for _ in range(25):
        tot = rng.randint(10, 100)
        rec = rng.randint(0, tot)
        res = segregate_mixed_lot_vendor_ti_hi_pallets(tot, rec)
        assert res["clean_cases"] + res["recalled_cases"] == tot
