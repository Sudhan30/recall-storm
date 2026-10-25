"""Property tests for recallstorm.recall_lots.mock_recall_generator."""
from recallstorm.recall_lots.mock_recall_generator import scale_scenario_store_count


def test_scale_scenario_store_count_props():
    base = ["WM1", "WM2", "WM3"]
    for k in range(1, 10):
        assert len(scale_scenario_store_count(base, k)) == 3 * k
