"""Edge tests for recallstorm.aliases.bundles."""
import pytest
from recallstorm.aliases.bundles import (
    bundle_match_path,
    component_ingredients,
    flatten_bundle,
    is_bundle,
    split_bundle,
)


def test_bundles_edge():
    assert split_bundle("") == []
    assert component_ingredients("A: SUGAR", "Missing") == ""
    assert bundle_match_path("A: WATER | B: SALT", "RED3") is None
    with pytest.raises(TypeError):
        is_bundle(None)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        flatten_bundle(123)  # type: ignore[arg-type]
