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


def test_gs1_ai_parsing():
    assert "01" in ai_table()
    elem = "(01)07502264930572(11)261001(17)270200(10)LOT26A(21)SER99"
    ais = parse_element_string(elem)
    assert ai_01(ais) == "07502264930572"
    assert ai_10(ais) == "LOT26A"
    assert ai_11(ais) == date(2026, 10, 1)
    assert ai_17(ais) == date(2027, 2, 28)  # DD=00 -> last day of Feb 2027
    assert ai_21(ais) == "SER99"
    assert validate_ai("01", "07502264930572") is True
    assert validate_ai("17", "270200") is True
    assert validate_ai("10", "LOT26A") is True
    rebuilt = build_element_string(ais)
    assert rebuilt == elem

    unbracketed = "01075022649305721727011510LOT99"
    ais2 = parse_element_string(unbracketed)
    assert ai_01(ais2) == "07502264930572"
    assert ai_10(ais2) == "LOT99"
