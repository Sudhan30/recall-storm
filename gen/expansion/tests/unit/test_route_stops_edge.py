"""Edge tests for recallstorm.route.stops."""
from datetime import datetime, timezone
import pytest
from recallstorm.route.stops import (
    merge_stops,
    stop_eta,
    stops_for_truck,
)


def test_stops_edge():
    assert merge_stops([]) == []
    with pytest.raises(ValueError):
        stop_eta(datetime(2026, 12, 31, tzinfo=timezone.utc), -1)
    with pytest.raises(TypeError):
        stops_for_truck("not_manifest")  # type: ignore[arg-type]
