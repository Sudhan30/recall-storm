"""Edge case tests for recallstorm.gs1.gtin."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.gs1.gtin import gtin8_to_14, gtin_check_digit, is_valid_gtin, normalize_gtin


def test_gtin_edge():
    assert is_valid_gtin("00073621007018") is False
    assert is_valid_gtin("ABC") is False
    with pytest.raises(DataValidationError):
        gtin_check_digit("123")
    with pytest.raises(DataValidationError):
        normalize_gtin("12345")
    with pytest.raises(DataValidationError):
        gtin8_to_14("123")
