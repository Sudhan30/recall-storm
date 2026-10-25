"""Edge tests for recallstorm.route.dispatch."""
from datetime import datetime, timezone
import pytest
from recallstorm.route.dispatch import (
    arrival_eta,
    depart_time,
    driver_hours,
    validate_dispatch,
)


def test_dispatch_edge():
    dt = datetime(2026, 12, 31, 8, 0, tzinfo=timezone.utc)
    with pytest.raises(TypeError):
        depart_time("not_truck")  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        arrival_eta(dt, -1, 10.0)
    with pytest.raises(ValueError):
        driver_hours([], -5.0)
    assert validate_dispatch([{"manifest_id": "M1", "driver_hours": 14.0}], 11.0) != []
