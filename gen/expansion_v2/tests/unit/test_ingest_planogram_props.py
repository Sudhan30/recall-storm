"""Property tests for recallstorm.ingest.planogram."""
import random
from recallstorm.ingest.planogram import merge_planograms, parse_planogram_row


def test_merge_planograms_conservation():
    rng = random.Random(42)
    rows = [
        {"store_id": "WM1", "sku_id": f"S{rng.randint(1, 5)}", "loc_code": "A01-1-1-1", "units": rng.randint(1, 20)}
        for _ in range(30)
    ]
    facings = [parse_planogram_row(r) for r in rows]
    merged = merge_planograms(facings)
    assert sum(f.units for f in merged) == sum(f.units for f in facings)
