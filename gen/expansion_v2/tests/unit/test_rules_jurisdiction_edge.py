"""Edge case tests for recallstorm.rules.jurisdiction."""
import pytest
from recallstorm.rules.jurisdiction import jurisdictions_for_state, state_name


def test_jurisdiction_edge():
    assert jurisdictions_for_state("US") == ("US",)
    with pytest.raises(ValueError):
        jurisdictions_for_state("")
    with pytest.raises(ValueError):
        state_name("XX")
