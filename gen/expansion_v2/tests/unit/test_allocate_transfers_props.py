"""Property tests for recallstorm.allocate.transfers."""
from datetime import datetime, timedelta
from recallstorm.allocate.transfers import dc_to_store_windows


def test_dc_to_store_windows_always_before_deadline():
    deadline = datetime.fromisoformat("2027-01-01T00:00:00-08:00")
    for hrs in range(1, 30):
        as_of = deadline - timedelta(hours=hrs)
        s_iso, e_iso = dc_to_store_windows(as_of, deadline)
        assert datetime.fromisoformat(s_iso) < datetime.fromisoformat(e_iso) < deadline
