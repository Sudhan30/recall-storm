"""Edge tests for recallstorm.rules.preemption."""
import pytest
from recallstorm.rules.preemption import (
    preemption_status,
    stricter_rule,
)


def test_preemption_edge():
    assert preemption_status(None, None) == "NONE"
    with pytest.raises(TypeError):
        stricter_rule("a", "b")  # type: ignore[arg-type]
