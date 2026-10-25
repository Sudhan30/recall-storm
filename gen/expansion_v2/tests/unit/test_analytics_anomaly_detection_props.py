"""Property tests for recallstorm.analytics.anomaly_detection."""
from recallstorm.analytics.anomaly_detection import score_store_submission_credibility_index


def test_credibility_index_non_increasing_props():
    scores = [score_store_submission_credibility_index(i) for i in range(6)]
    for i in range(1, len(scores)):
        assert scores[i] <= scores[i - 1]
        assert 0.0 <= scores[i] <= 100.0
