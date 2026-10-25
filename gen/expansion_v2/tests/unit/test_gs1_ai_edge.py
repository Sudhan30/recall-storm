"""Edge case tests for recallstorm.gs1.ai."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.gs1.ai import parse_element_string, validate_ai


def test_gs1_ai_edge():
    # Unparenthesized with FNC1 (\x1d)
    raw = "]C101000736210070171727011510LOT1\x1d21SN1"
    ais = parse_element_string(raw)
    assert ais["10"] == "LOT1" and ais["21"] == "SN1"
    assert validate_ai("17", "999999") is False
    with pytest.raises(DataValidationError):
        parse_element_string("")
