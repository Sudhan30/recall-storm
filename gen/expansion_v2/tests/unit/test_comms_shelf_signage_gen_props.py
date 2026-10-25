"""Property tests for recallstorm.comms.shelf_signage_gen."""
from datetime import date
from recallstorm.comms.shelf_signage_gen import schedule_fourteen_day_sign_takedown


def test_takedown_date_strictly_after_posted():
    for d in range(1, 20):
        posted = f"2027-01-{d:02d}"
        takedown = schedule_fourteen_day_sign_takedown(posted, 14)
        assert (date.fromisoformat(takedown) - date.fromisoformat(posted)).days == 14
