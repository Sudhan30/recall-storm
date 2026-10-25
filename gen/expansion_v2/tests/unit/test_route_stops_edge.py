"""Edge case tests for recallstorm.route.stops."""
from datetime import datetime
import pytest
from recallstorm.route.stops import merge_stops, route_distance, stop_eta


def test_route_stops_edge():
    assert merge_stops([]) == []
    assert route_distance([], {}) == 0.0
    with pytest.raises(ValueError):
        stop_eta(datetime(2026, 12, 31, 8, 0), -1)
