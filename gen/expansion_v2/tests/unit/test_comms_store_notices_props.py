"""Property tests for recallstorm.comms.store_notices."""
import random
from recallstorm.comms.store_notices import track_store_manager_read_receipt_ack


def test_read_receipt_sla_props():
    rng = random.Random(42)
    for _ in range(25):
        m = rng.uniform(0.0, 30.0)
        assert track_store_manager_read_receipt_ack("WM1", m)["within_sla"] == (m <= 15.0)
