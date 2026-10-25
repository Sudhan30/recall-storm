"""Edge tests for recallstorm.allocate.priority."""
import pytest
from recallstorm.allocate.priority import (
    deadline_weight,
    store_priority,
)


def test_priority_edge():
    assert deadline_weight(0.0) == 10.0
    assert deadline_weight(-5.0) == 10.0
    with pytest.raises(TypeError):
        store_priority("not_store")  # type: ignore[arg-type]
