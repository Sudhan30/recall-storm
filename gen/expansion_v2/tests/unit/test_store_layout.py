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


def test_store_layout():
    l1 = Location("A01", 1, 1, 1)
    l2 = Location("A03", 5, 2, 1)
    assert bay_coordinates("A01", 1) == (4.0, 2.5)
    assert location_xy(l1) == (4.0, 2.5)
    assert walking_distance(l1, l2) == 18.0
    assert aisle_order([l2, l1]) == [l1, l2]
    assert nearest_location(l1, [l2, l1]) == l1

    st = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    lay = build_layout(st, [Facing("WM1", "S1", l1, 5), Facing("WM1", "S2", l2, 5)])
    assert isinstance(lay, StoreLayout)
    assert layout_bounds(lay) == (12.0, 12.5)
    assert "WM1" in layout_to_json(lay)
