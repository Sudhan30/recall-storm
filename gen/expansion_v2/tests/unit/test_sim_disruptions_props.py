"""Property tests for recallstorm.sim.disruptions."""
from contract import Store, StoreFormat
from recallstorm.sim.disruptions import seed_disruptions


def test_seed_disruptions_determinism():
    stores = [Store(f"WM{i}", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles") for i in range(10)]
    assert seed_disruptions(stores, 99) == seed_disruptions(list(reversed(stores)), 99)
