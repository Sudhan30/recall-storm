"""Edge tests for recallstorm.adjudicate.evidence."""
import pytest
from recallstorm.adjudicate.evidence import (
    build_evidence,
    highlight_match,
    validate_evidence,
)


def test_evidence_edge():
    with pytest.raises(ValueError):
        highlight_match("ABC", 0, 10)
    with pytest.raises(TypeError):
        build_evidence("a", "b", "c")  # type: ignore[arg-type]
    assert validate_evidence({"type": "evidence", "source_span": [5, 1]}) != []
