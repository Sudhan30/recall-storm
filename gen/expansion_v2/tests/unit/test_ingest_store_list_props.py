"""Property tests for recallstorm.ingest.store_list."""
import random
from recallstorm.ingest.store_list import store_from_row, validate_store_list


def test_store_from_row_props():
    rng = random.Random(42)
    stores = [
        store_from_row(
            {
                "store_id": f"WM{1000 + i}",
                "format": rng.choice(["SUPERCENTER", "DISCOUNT", "NEIGHBORHOOD", "SAMS"]),
                "lat": rng.uniform(32.5, 41.5),
                "lon": rng.uniform(-122.5, -117.0),
            }
        )
        for i in range(25)
    ]
    assert validate_store_list(stores) == []
