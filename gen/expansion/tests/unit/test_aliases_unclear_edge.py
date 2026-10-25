"""Edge tests for recallstorm.aliases.unclear."""
import pytest
from recallstorm.aliases.unclear import (
    is_generic_color,
    is_unreadable,
    readability_score,
    redact_noise,
)


def test_unclear_edge():
    assert is_unreadable("") is True
    assert readability_score("") == 0.0
    assert is_generic_color("COLOR (ANNATTO)") is False
    with pytest.raises(TypeError):
        redact_noise(None)  # type: ignore[arg-type]
