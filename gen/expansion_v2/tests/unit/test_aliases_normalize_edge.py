"""Edge case tests for recallstorm.aliases.normalize."""
import pytest
from recallstorm.aliases.normalize import (
    denormalize_span,
    normalize_ingredients,
    split_sub_ingredients,
    tokenize_ingredients,
)


def test_normalize_edge():
    assert tokenize_ingredients("") == []
    assert split_sub_ingredients("   ") == []
    assert denormalize_span("ABC", (-5, 99)) == (0, 3)
    with pytest.raises(TypeError):
        normalize_ingredients(None)  # type: ignore[arg-type]
