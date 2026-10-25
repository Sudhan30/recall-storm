"""Edge tests for recallstorm.aliases.detect."""
import pytest
from recallstorm.aliases.detect import (
    explain_match,
    find_first_match,
    find_matches,
    match_confidence,
    match_span,
)


def test_detect_edge():
    assert find_matches("", "RED3") == []
    assert find_first_match("WATER, SALT", "RED3") is None
    m = find_first_match("CONTAINS SPECIAL_DYE_X", "CUSTOM", extra_aliases=["SPECIAL_DYE_X"])
    assert m is not None and m.match_text == "SPECIAL_DYE_X"
    with pytest.raises(TypeError):
        match_span("not_match")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        match_confidence("not_match")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        explain_match("not_match")  # type: ignore[arg-type]
