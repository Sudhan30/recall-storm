"""Property tests for recallstorm.ingest.recall_feeds."""
import random
from recallstorm.ingest.recall_feeds import merge_recall_sources


def test_merge_recall_sources_idempotent():
    rng = random.Random(42)
    items = [
        {"recall_id": f"R-{rng.randint(1, 15)}", "date": f"2026-01-{rng.randint(10, 28)}", "states": ["US"]}
        for _ in range(40)
    ]
    m1 = merge_recall_sources(items)
    m2 = merge_recall_sources(m1, items)
    assert m1 == m2
