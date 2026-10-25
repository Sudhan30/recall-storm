"""Property tests for recallstorm.recall_lots.lot_pattern_matcher."""
from recallstorm.recall_lots.lot_pattern_matcher import score_lot_string_similarity


def test_lot_similarity_reflexive_and_bounded():
    for s in ("L2601", "BATCH99A", "20261230"):
        assert score_lot_string_similarity(s, s) == 1.0
        assert 0.0 <= score_lot_string_similarity(s, "OTHER") <= 1.0
