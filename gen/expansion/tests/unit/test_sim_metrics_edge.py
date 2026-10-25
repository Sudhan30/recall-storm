"""Edge tests for recallstorm.sim.metrics."""
from recallstorm.sim.metrics import (
    district_completion,
    idle_minutes,
    store_completion,
)


def test_metrics_edge():
    assert store_completion([], "WM1") == 1.0
    assert district_completion([], {}, "D01") == 1.0
    assert idle_minutes([], "A1") == 0.0
