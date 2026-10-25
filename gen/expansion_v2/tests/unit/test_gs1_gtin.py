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
    # Sample from data/skus.jsonl: 00073621007017
    g14 = "00073621007017"
    assert gtin_check_digit(g14[:-1]) == 7
    assert is_valid_gtin(g14) is True
    assert gtin8_to_14("12345670") == "00000012345670"
    assert gtin12_to_14("073621007017") == g14
    assert gtin13_to_14("0073621007017") == g14
    assert normalize_gtin("073621007017") == g14
    assert gtin_indicator(g14) == "0"
    assert gtin_company_prefix(g14, 6) == "007362"
    assert len(gtin_variants(g14)) == 3
