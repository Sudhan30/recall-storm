"""Edge tests for recallstorm.rules.scope."""
import pytest
from recallstorm.rules.scope import (
    is_food_scope,
    sku_in_scope,
)


def test_scope_edge():
    with pytest.raises(TypeError):
        is_food_scope("not_sku")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        sku_in_scope("not_sku", "not_rule")  # type: ignore[arg-type]
