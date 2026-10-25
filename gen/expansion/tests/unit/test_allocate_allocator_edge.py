"""Edge tests for recallstorm.allocate.allocator."""
import pytest
from contract import DcStock, Store, StoreFormat
from recallstorm.allocate.allocator import allocate_substitutes


def test_allocator_edge():
    st1 = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    assert allocate_substitutes({("WM1", "SUB_NONE"): 5}, [DcStock("DC1", "SUB1", 5)], [st1]) == []
    assert allocate_substitutes({("WM1", "SUB1"): 0}, [DcStock("DC1", "SUB1", 5)], [st1]) == []
    with pytest.raises(TypeError):
        allocate_substitutes("bad", [], [])  # type: ignore[arg-type]
