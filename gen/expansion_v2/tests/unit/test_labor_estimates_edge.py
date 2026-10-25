"""Edge case tests for recallstorm.labor.estimates."""
import pytest
from recallstorm.labor.estimates import place_minutes, pull_minutes, tag_minutes, walk_minutes


def test_labor_estimates_edge():
    with pytest.raises(ValueError):
        pull_minutes(-1)
    with pytest.raises(ValueError):
        place_minutes(-1)
    with pytest.raises(ValueError):
        tag_minutes(-1)
    with pytest.raises(ValueError):
        walk_minutes(-5.0)
