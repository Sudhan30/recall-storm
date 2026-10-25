"""Property tests for recallstorm.store.formats."""
from contract import StoreFormat
from recallstorm.store.formats import format_backroom_capacity, format_labor_minutes, format_priority


def test_all_store_formats_have_positive_metrics():
    for fmt in StoreFormat:
        assert format_labor_minutes(fmt) > 0
        assert format_backroom_capacity(fmt) > 0
        assert 1 <= format_priority(fmt) <= 4
