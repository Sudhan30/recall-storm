"""Property tests for recallstorm.governance.third_party_audits."""
import random
from recallstorm.governance.third_party_audits import score_banner_integrity_gap_percentage


def test_integrity_gap_pct_bounds():
    rng = random.Random(42)
    for _ in range(25):
        tot = rng.randint(1, 100)
        gap = rng.randint(0, tot)
        pct = score_banner_integrity_gap_percentage(gap, tot)
        assert 0.0 <= pct <= 100.0
