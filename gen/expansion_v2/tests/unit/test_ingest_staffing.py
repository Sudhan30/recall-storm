"""Unit tests for recallstorm.ingest.staffing."""
from recallstorm.ingest.staffing import (
    floater_pool,
    overnight_shift_window,
    parse_roster_row,
    parse_shift,
    roster_by_district,
    roster_by_store,
    roster_to_associates,
    shift_minutes,
    validate_roster,
)


def test_staffing_functions():
    r1 = {
        "associate_id": "WM1563-A01",
        "store_id": "WM1563",
        "district": "D06",
        "is_floater": False,
        "shift_start": "2026-12-30T22:00:00-08:00",
        "shift_end": "2026-12-31T06:00:00-08:00",
    }
    r2 = {
        "associate_id": "FLT-D06-01",
        "store_id": None,
        "district": "D06",
        "is_floater": True,
        "shift_start": "2026-12-30T22:00:00-08:00",
        "shift_end": "2026-12-31T06:00:00-08:00",
    }
    a1 = parse_roster_row(r1)
    assert shift_minutes(a1) == 480.0
    assocs = roster_to_associates([r1, r2])
    assert len(floater_pool(assocs, "D06")) == 1
    assert "WM1563" in roster_by_store(assocs)
    assert len(roster_by_district(assocs)["D06"]) == 2
    s, e = overnight_shift_window("2026-12-30")
    assert parse_shift(s.isoformat(), e.isoformat()) == (s, e)
    assert validate_roster(assocs) == []
