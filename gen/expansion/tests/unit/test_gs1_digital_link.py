"""Unit tests for recallstorm.gs1.digital_link."""
from datetime import date
from recallstorm.gs1.digital_link import (
    ais_to_digital_link,
    build_digital_link,
    canonical_digital_link,
    digital_link_expiry,
    digital_link_gtin,
    digital_link_lot,
    digital_link_to_ais,
    is_digital_link,
    parse_digital_link,
)


def test_digital_link_roundtrip():
    uri = build_digital_link("7502264930572", lot="L2601A", expiry="270115", serial="S01")
    assert is_digital_link(uri) is True
    assert digital_link_gtin(uri) == "07502264930572"
    assert digital_link_lot(uri) == "L2601A"
    assert digital_link_expiry(uri) == date(2027, 1, 15)
    ais = digital_link_to_ais(uri)
    assert parse_digital_link(uri) == ais
    assert ais_to_digital_link(ais) == canonical_digital_link(uri)
