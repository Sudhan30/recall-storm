"""Property tests for recallstorm.recall_lots.best_by_window."""
import random
from recallstorm.recall_lots.best_by_window import (
    calculate_shelf_life_backdate_lot,
    check_freeze_by_extension,
)


def test_backdate_and_extension_inverse_props():
    rng = random.Random(42)
    base = "2026-06-15"
    for _ in range(25):
        days = rng.randint(1, 365)
        ext = check_freeze_by_extension(base, days)
        assert calculate_shelf_life_backdate_lot(ext, days) == base
