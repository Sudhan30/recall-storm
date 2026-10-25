"""Edge tests for recallstorm.gs1.digital_link."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.gs1.digital_link import (
    ais_to_digital_link,
    is_digital_link,
    parse_digital_link,
)


def test_digital_link_edge():
    assert is_digital_link("not_a_uri") is False
    assert is_digital_link("https://example.com/no_ai") is False
    with pytest.raises(DataValidationError):
        parse_digital_link("https://example.com/no_ai")
    with pytest.raises(DataValidationError):
        ais_to_digital_link({})
