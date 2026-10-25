"""Edge case tests for recallstorm.store.layout."""
from contract import Location
from recallstorm.store.layout import StoreLayout, layout_bounds, nearest_location


def test_store_layout_edge():
    assert nearest_location(Location("A01", 1, 1, 1), []) is None
    assert layout_bounds(StoreLayout("WM1", [])) == (0.0, 0.0)
