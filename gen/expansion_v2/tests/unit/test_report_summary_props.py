"""Property tests for recallstorm.report.summary."""
from recallstorm.report.summary import counts_by_verdict


def test_counts_by_verdict_sum_matches_verdict_records():
    recs = [
        {"type": "sku_verdict", "sku_id": f"S{i}", "verdict": "PULL" if i % 3 == 0 else "KEEP"}
        for i in range(21)
    ]
    c = counts_by_verdict(recs)
    assert sum(c.values()) == 21
