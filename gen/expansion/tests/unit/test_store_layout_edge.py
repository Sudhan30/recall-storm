"""Edge tests for recallstorm.store.layout."""
import pytest
from contract import Location
from recallstorm.store.layout import (
    StoreLayout,
    bay_coordinates,
    layout_bounds,
    nearest_location,
)


def test_layout_edge():
    assert layout_bounds(StoreLayout("WM1", ())) == (0.0, 0.0, 0.0, 0.0)
    with pytest.raises(ValueError):
        nearest_location(Location("A01", 1, 1, 1), [])
    with pytest.raises(ValueError):
        bay_coordinates("", 1)
