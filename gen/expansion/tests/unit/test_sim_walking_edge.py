"""Edge tests for recallstorm.sim.walking."""
import pytest
from contract import Location
from recallstorm.sim.walking import (
    shortest_path,
    walk_seconds,
    walking_summary,
)


def test_walking_edge():
    loc = Location("A01", 1, 1, 1)
    assert shortest_path(loc, loc) == [loc]
    assert walking_summary([])["total_distance_ft"] == 0.0
    with pytest.raises(ValueError):
        walk_seconds(loc, loc, 0.0)
