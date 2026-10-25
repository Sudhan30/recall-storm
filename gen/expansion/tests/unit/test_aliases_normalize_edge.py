"""Edge tests for recallstorm.aliases.normalize."""
import pytest
from recallstorm.aliases.normalize import (
    denormalize_span,
    normalize_ingredients,
)


def test_normalize_edge():
    with pytest.raises(TypeError):
        normalize_ingredients(None)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        denormalize_span("abc", 5, 2)
    assert denormalize_span("abc", 1, 10) == (1, 3)
