"""Edge tests for recallstorm.ingest.open_food_facts."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.ingest.open_food_facts import (
    merge_off_fdc,
    off_gtin,
    parse_off_product,
)


def test_off_edge():
    with pytest.raises(DataValidationError):
        off_gtin({})
    with pytest.raises(DataValidationError):
        parse_off_product("not_dict")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        merge_off_fdc("a", "b")  # type: ignore[arg-type]
