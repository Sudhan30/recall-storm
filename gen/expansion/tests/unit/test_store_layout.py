"""Unit tests for recallstorm.store.layout."""
from contract import Facing, Location, Store, StoreFormat
from recallstorm.store.layout import (
    StoreLayout,
    aisle_order,
    bay_coordinates,
    build_layout,
    layout_bounds,
    layout_to_json,
    location_xy,
    nearest_location,
    walking_distance,
)


def test_layout_and_walking():
    l1 = Location("A01", 1, 1, 1)
    l2 = Location("A01", 5, 1, 1)
    l3 = Location("A02", 5, 1, 1)
    assert bay_coordinates("A01", 1) == (12.0, 4.0)
    assert location_xy(l1) == (12.0, 4.5)
    assert walking_distance(l1, l2) == 16.0
    assert walking_distance(l1, l3) > 16.0
    assert nearest_location(l1, [l2, l3]) == l2
    ordered = aisle_order([l3, l2, l1])
    assert ordered[0] == l1
    st = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    lay = build_layout(st, [Facing("WM1", "S1", l1, 10), Facing("WM1", "S2", l3, 10)])
    assert isinstance(lay, StoreLayout)
    assert layout_bounds(lay)[2] == 24.0
    assert "WM1" in layout_to_json(lay)
