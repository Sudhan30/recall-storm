"""Property tests for recallstorm.core.validate."""
import random
from contract import Sku
from recallstorm.core.validate import validate_sku


def test_validate_sku_props():
    rng = random.Random(42)
    for i in range(30):
        units = rng.randint(1, 48)
        cube = rng.uniform(0.5, 5.0)
        weight = rng.uniform(1.0, 40.0)
        sku = Sku(f"SKU{i}", f"{i:014d}", "Name", "Brand", "cat", "ING", True, False, units, cube, weight)
        assert validate_sku(sku) == []
