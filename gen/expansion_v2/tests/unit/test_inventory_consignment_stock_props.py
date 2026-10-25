"""Property tests for recallstorm.inventory.consignment_stock."""
import random
from recallstorm.inventory.consignment_stock import exclude_consignment_from_shrink_gl


def test_exclude_consignment_conservation_props():
    rng = random.Random(42)
    for _ in range(25):
        tot = rng.uniform(100.0, 1000.0)
        sbt = rng.uniform(0.0, tot)
        rem = exclude_consignment_from_shrink_gl(tot, sbt)
        assert abs((rem + sbt) - tot) <= 0.02
