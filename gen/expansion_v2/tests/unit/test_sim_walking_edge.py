"""Edge case tests for recallstorm.sim.walking."""
import pytest
from contract import Location
from recallstorm.sim.walking import shortest_path, walk_seconds, walking_summary


def test_sim_walking_edge():
    l1 = Location("A01", 1, 1, 1)
    assert shortest_path(l1, l1) == [l1]
    assert walking_summary([])["total_distance_m"] == 0.0
    with pytest.raises(ValueError):
        walk_seconds(l1, l1, 0.0)
