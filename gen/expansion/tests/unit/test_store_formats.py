"""Unit tests for recallstorm.store.formats."""
from contract import Action, Store, StoreFormat
from recallstorm.store.formats import (
    carries_category,
    format_backroom_capacity,
    format_labor_minutes,
    format_priority,
    format_profile,
    format_summary,
    format_tag_rule,
    formats_in_pack,
    is_club_format,
)


def test_store_formats():
    assert format_profile(StoreFormat.SUPERCENTER)["priority"] == 1
    assert is_club_format(StoreFormat.SAMS) is True
    assert format_priority(StoreFormat.SUPERCENTER) == 1
    assert format_backroom_capacity(StoreFormat.SAMS) == 500
    assert format_tag_rule(StoreFormat.SAMS) == "PALLET_PLACARD"
    assert format_labor_minutes(StoreFormat.SUPERCENTER, Action.PLACE_SUB) == 4.0
    assert carries_category(StoreFormat.NEIGHBORHOOD, "candy") is True

    st = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    assert formats_in_pack([st]) == [StoreFormat.SUPERCENTER]
    assert format_summary([st]) == {"SUPERCENTER": 1}
