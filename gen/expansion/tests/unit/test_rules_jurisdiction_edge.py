"""Edge tests for recallstorm.rules.jurisdiction."""
import pytest
from recallstorm.core.errors import RuleConfigError
from recallstorm.rules.jurisdiction import (
    applies_in_state,
    jurisdictions_for_state,
    state_name,
)


def test_jurisdiction_edge():
    assert jurisdictions_for_state("US") == ("US",)
    with pytest.raises(RuleConfigError):
        state_name("XX")
    with pytest.raises(RuleConfigError):
        jurisdictions_for_state("")
    with pytest.raises(TypeError):
        applies_in_state("not_rule", "CA")  # type: ignore[arg-type]
