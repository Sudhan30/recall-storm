"""Property tests for recallstorm.governance.regulatory_calendar."""
from datetime import date, timedelta
from recallstorm.governance.regulatory_calendar import calculate_working_days_to_mandatory_ban


def test_working_days_never_exceed_calendar_days():
    d0 = date(2026, 12, 1)
    for k in range(1, 35):
        dk = d0 + timedelta(days=k)
        wd = calculate_working_days_to_mandatory_ban(d0.isoformat(), dk.isoformat())
        assert 0 <= wd <= k
