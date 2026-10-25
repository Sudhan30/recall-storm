"""Edge tests for recallstorm.adjudicate.sampling."""
import pytest
from recallstorm.adjudicate.sampling import (
    estimate_error_rate,
    resample,
    review_rate,
    sample_for_review,
)


def test_sampling_edge():
    assert resample([], 5) == []
    with pytest.raises(ValueError):
        sample_for_review([], -1)
    with pytest.raises(ValueError):
        review_rate(1, 0)
    with pytest.raises(ValueError):
        estimate_error_rate(5, 2)
