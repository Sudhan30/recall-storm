"""Property tests for recallstorm.rules.carb_voc."""
from datetime import datetime
import random
from contract import Sku, Verdict
from recallstorm.rules.carb_voc import evaluate_voc


def test_carb_voc_threshold_props():
    rng = random.Random(42)
    for _ in range(25):
        pct = round(rng.uniform(5.0, 45.0), 1)
        sku = Sku("L", "00012345678905", "Lubricant", "B", "lubricant", f"OIL, VOC: {pct}%", False, False, 12, 1.0, 8.0)
        dec = evaluate_voc(sku, "CA", datetime(2026, 1, 1))
        assert (dec.verdict == Verdict.PULL) == (pct > 25.0)
