"""Property tests for recallstorm.ingest.staffing."""
from recallstorm.ingest.staffing import overnight_shift_window, parse_roster_row, shift_minutes


def test_staffing_shift_minutes_props():
    for day in range(10, 30):
        s, e = overnight_shift_window(f"2026-12-{day:02d}")
        a = parse_roster_row(
            {
                "associate_id": f"A{day}",
                "store_id": "WM1",
                "district": "D01",
                "is_floater": False,
                "shift_start": s.isoformat(),
                "shift_end": e.isoformat(),
            }
        )
        assert shift_minutes(a) == 480.0
