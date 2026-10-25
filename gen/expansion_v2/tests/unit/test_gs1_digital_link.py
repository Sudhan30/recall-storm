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


def test_digital_link():
    uri = build_digital_link("073621007017", lot="L26A", expiry="270115", serial="S1", domain="https://example.com")
    assert is_digital_link(uri) is True
    ais = parse_digital_link(uri)
    assert digital_link_to_ais(uri) == ais
    assert digital_link_gtin(uri) == "00073621007017"
    assert digital_link_lot(uri) == "L26A"
    assert digital_link_expiry(uri) == date(2027, 1, 15)
    canon = canonical_digital_link(uri)
    assert canon.startswith("https://id.gs1.org/01/00073621007017")
    assert ais_to_digital_link(ais) == canon
