"""Edge case tests for recallstorm.allocate.allocator."""
from contract import DcStock, Store, StoreFormat
from recallstorm.allocate.allocator import allocate_substitutes


def test_allocate_allocator_edge():
    s1 = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    assert allocate_substitutes({}, [DcStock("DC1", "S1", 5)], [s1]) == []
    assert allocate_substitutes({("WM1", "S1"): 5}, [DcStock("DC1", "S1", 0)], [s1]) == []
    assert allocate_substitutes({("WM1", "S1"): 0}, [DcStock("DC1", "S1", 5)], [s1]) == []
