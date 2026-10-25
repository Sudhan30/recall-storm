"""Edge case tests for recallstorm.route.dispatch."""
from datetime import datetime
import pytest
from contract import RouteManifest, Stop
from recallstorm.route.dispatch import driver_hours, validate_dispatch


def test_route_dispatch_edge():
    with pytest.raises(ValueError):
        driver_hours(-1)
    mnf = RouteManifest("M1", "UNKNOWN-TRK", "DC1", (Stop("WM1", 1, 1.0, 1.0),), datetime(2026, 12, 31, 8, 0))
    assert len(validate_dispatch([mnf], {})) == 1
