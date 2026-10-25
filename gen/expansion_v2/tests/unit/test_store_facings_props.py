"""Property tests for recallstorm.store.facings."""
import random
from contract import Facing, Location
from recallstorm.store.facings import group_facings, units_on_shelf


def test_group_facings_unit_conservation():
    rng = random.Random(42)
    facings = [
        Facing(f"WM{rng.randint(1, 3)}", f"S{rng.randint(1, 4)}", Location("A01", i, 1, 1), rng.randint(1, 30))
        for i in range(1, 25)
    ]
    grouped = group_facings(facings)
    assert sum(sum(f.units for f in flist) for flist in grouped.values()) == units_on_shelf(facings)
