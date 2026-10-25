"""Unit tests for recallstorm.store.formats."""
from contract import Store, StoreFormat
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
    assert is_club_format(StoreFormat.SAMS) is True
    assert is_club_format(StoreFormat.SUPERCENTER) is False
    assert format_profile(StoreFormat.SUPERCENTER)["priority"] == 1
    assert carries_category(StoreFormat.SUPERCENTER, "candy") is True
    assert carries_category(StoreFormat.NEIGHBORHOOD, "automotive") is False
    assert format_labor_minutes(StoreFormat.SUPERCENTER) == 480.0
    assert format_tag_rule(StoreFormat.SAMS) == "PALLET_SIGN"
    assert format_backroom_capacity(StoreFormat.SAMS) == 900
    assert format_priority(StoreFormat.SUPERCENTER) < format_priority(StoreFormat.NEIGHBORHOOD)
    s1 = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    s2 = Store("SAMS1", StoreFormat.SAMS, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    assert formats_in_pack([s2, s1]) == [StoreFormat.SUPERCENTER, StoreFormat.SAMS]
    assert format_summary([s1, s2])["SAMS"] == 1
