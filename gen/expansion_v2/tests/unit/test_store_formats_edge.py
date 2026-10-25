"""Edge case tests for recallstorm.store.formats."""
import pytest
from recallstorm.store.formats import format_profile, format_summary, formats_in_pack


def test_store_formats_edge():
    assert formats_in_pack([]) == []
    assert sum(format_summary([]).values()) == 0
    with pytest.raises(ValueError):
        format_profile("INVALID")  # type: ignore[arg-type]
