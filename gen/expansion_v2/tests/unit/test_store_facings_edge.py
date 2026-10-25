"""Edge case tests for recallstorm.store.facings."""
from recallstorm.store.facings import facings_for_store, facings_summary, locate_sku, units_on_shelf


def test_store_facings_edge():
    assert facings_for_store([], "WM1") == []
    assert locate_sku([], "WM1", "S1") == []
    assert units_on_shelf([]) == 0
    assert facings_summary([])["total_units"] == 0
