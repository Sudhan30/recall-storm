"""Unit tests for recallstorm.gs1.ai."""
from datetime import date
from recallstorm.gs1.ai import (
    ai_01,
    ai_10,
    ai_11,
    ai_17,
    ai_21,
    ai_table,
    build_element_string,
    parse_element_string,
    validate_ai,
)


def test_gs1_ai():
    assert "01" in ai_table()
    s = "(01)00073621007017(17)270200(11)260615(10)LOT26A(21)SER99"
    ais = parse_element_string(s)
    assert ai_01(ais) == "00073621007017"
    assert ai_17(ais) == date(2027, 2, 28)  # DD=00 -> last day of Feb 2027
    assert ai_11(ais) == date(2026, 6, 15)
    assert ai_10(ais) == "LOT26A"
    assert ai_21(ais) == "SER99"
    assert validate_ai("01", "00073621007017") is True
    assert validate_ai("17", "270200") is True
    rebuilt = build_element_string(ais)
    assert rebuilt == s
