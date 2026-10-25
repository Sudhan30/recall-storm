"""Edge tests for recallstorm.rules.dates."""
from datetime import datetime
import pytest
from contract import Rule
from recallstorm.rules.dates import (
    effective_at,
    next_effective_rule,
)


def test_dates_edge():
    rule = Rule("R1", "RED3", ("Red 3",), ("CA",), ("food",), datetime(2027, 1, 1, 0, 0, 0), "c", "s")
    assert effective_at(rule, datetime(2027, 1, 1, 0, 0, 0)) is True
    assert next_effective_rule([rule], datetime(2028, 1, 1, 0, 0, 0)) is None
    with pytest.raises(TypeError):
        effective_at("not_rule", datetime(2027, 1, 1))  # type: ignore[arg-type]
