"""Edge tests for recallstorm.gs1.ai."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.gs1.ai import (
    build_element_string,
    parse_element_string,
    validate_ai,
)


def test_gs1_ai_edge():
    assert validate_ai("17", "261301") is False
    assert validate_ai("99", "val") is False
    with pytest.raises(DataValidationError):
        parse_element_string("")
    with pytest.raises(DataValidationError):
        parse_element_string("99INVALID")
    with pytest.raises(DataValidationError):
        build_element_string({})
