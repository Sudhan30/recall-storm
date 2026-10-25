"""Property tests for recallstorm.vendor.supplier_scorecards."""
import random
from recallstorm.vendor.supplier_scorecards import calculate_recall_frequency_severity_index


def test_class_i_weighs_more_than_class_ii():
    rng = random.Random(42)
    for _ in range(25):
        n = rng.randint(1, 20)
        assert calculate_recall_frequency_severity_index(n, 0, 0) > calculate_recall_frequency_severity_index(0, n, 0)
