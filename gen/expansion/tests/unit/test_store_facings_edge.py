"""Edge tests for recallstorm.store.facings."""
from recallstorm.store.facings import (
    affected_facings,
    facings_for_store,
    locate_sku,
    units_on_shelf,
)


def test_facings_edge():
    assert facings_for_store([], "WM1") == []
    assert affected_facings([], {}) == []
    assert units_on_shelf([], "WM1") == 0
    assert locate_sku([], "WM1", "S1") == []
