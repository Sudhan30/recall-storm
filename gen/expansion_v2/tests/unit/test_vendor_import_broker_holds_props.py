"""Property tests for recallstorm.vendor.import_broker_holds."""
import random
from recallstorm.vendor.import_broker_holds import calculate_port_demurrage_detention_fees


def test_demurrage_fees_linear_props():
    rng = random.Random(42)
    for _ in range(25):
        d = rng.randint(0, 30)
        assert calculate_port_demurrage_detention_fees(d, 200.0) == d * 200.0
