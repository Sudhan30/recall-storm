"""Unit tests for recallstorm.gs1.gtin."""
from recallstorm.gs1.gtin import (
    gtin8_to_14,
    gtin12_to_14,
    gtin13_to_14,
    gtin_check_digit,
    gtin_company_prefix,
    gtin_indicator,
    gtin_variants,
    is_valid_gtin,
    normalize_gtin,
)


def test_gtin_functions():
    # 07502264930572: payload 0750226493057 -> check digit 2
    assert gtin_check_digit("0750226493057") == 2
    assert is_valid_gtin("07502264930572") is True
    assert is_valid_gtin("07502264930579") is False
    assert gtin8_to_14("12345670") == "00000012345670"
    assert gtin12_to_14("073621007017") == "00073621007017"
    assert gtin13_to_14("7502264930572") == "07502264930572"
    assert normalize_gtin("736210070170") == "00736210070170"
    assert gtin_indicator("00073621007017") == "0"
    assert len(gtin_company_prefix("00073621007017")) == 7
    assert "073621007017" in gtin_variants("00073621007017")
