"""Property tests for recallstorm.analytics.root_cause_mining."""
from recallstorm.analytics.root_cause_mining import rank_top_ten_systemic_execution_barriers


def test_top_ten_barriers_capped_at_ten():
    barriers = {f"B{i:02d}": i for i in range(25)}
    top = rank_top_ten_systemic_execution_barriers(barriers)
    assert len(top) == 10
    assert top[0] == "B24"
