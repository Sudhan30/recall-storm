"""Edge case tests for recallstorm.gs1.digital_link."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.gs1.digital_link import ais_to_digital_link, is_digital_link, parse_digital_link


def test_digital_link_edge():
    assert is_digital_link("ftp://bad") is False
    with pytest.raises(DataValidationError):
        parse_digital_link("https://example.com/no_gtin")
    with pytest.raises(DataValidationError):
        ais_to_digital_link({"10": "LOT1"})
