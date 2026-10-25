"""Edge case tests for recallstorm.adjudicate.sampling."""
import pytest
from recallstorm.adjudicate.sampling import confidence_interval, estimate_error_rate, sample_for_review


def test_sampling_edge():
    with pytest.raises(ValueError):
        sample_for_review([], 1.5)
    with pytest.raises(ValueError):
        estimate_error_rate(5, 10)
    assert estimate_error_rate(0, 0) == 0.0
    assert confidence_interval(0.5, 0) == (0.0, 1.0)
