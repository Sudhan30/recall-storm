"""Edge tests for recallstorm.store.signage."""
import pytest
from recallstorm.store.signage import (
    sign_language,
    tag_flash_text,
)


def test_signage_edge():
    assert sign_language("MN") == "en"
    with pytest.raises(TypeError):
        tag_flash_text("not_sku", [])  # type: ignore[arg-type]
