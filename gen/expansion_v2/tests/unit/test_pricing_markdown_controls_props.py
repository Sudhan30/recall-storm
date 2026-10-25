"""Property tests for recallstorm.pricing.markdown_controls."""
import random
from recallstorm.pricing.markdown_controls import flag_suspicious_pre_recall_markdowns


def test_suspicious_markdown_threshold_props():
    rng = random.Random(42)
    for _ in range(25):
        pct = rng.uniform(0.0, 100.0)
        assert flag_suspicious_pre_recall_markdowns("WM1", pct)["flagged"] == (pct >= 50.0)
