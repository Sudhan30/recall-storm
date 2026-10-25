"""Edge tests for recallstorm.store.formats."""
import pytest
from contract import StoreFormat
from recallstorm.store.formats import (
    carries_category,
    format_profile,
)


def test_formats_edge():
    assert carries_category(StoreFormat.DISCOUNT, "") is False
    with pytest.raises(ValueError):
        format_profile("INVALID_FMT")
