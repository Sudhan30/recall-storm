"""Property tests for recallstorm.core.clock."""
from datetime import datetime, timedelta
import random
from recallstorm.core.clock import iso_with_offset, minutes_between


def test_minutes_between_antisymmetry():
    rng = random.Random(42)
    base = datetime.fromisoformat("2026-12-30T18:00:00-08:00")
    for _ in range(30):
        delta = rng.randint(1, 5000)
        later = base + timedelta(minutes=delta)
        assert minutes_between(base, later) == float(delta)
        assert minutes_between(later, base) == float(-delta)
        assert "+" in iso_with_offset(later) or "-" in iso_with_offset(later)
