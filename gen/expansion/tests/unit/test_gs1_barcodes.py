"""Unit tests for recallstorm.gs1.barcodes."""
from recallstorm.gs1.barcodes import (
    ScanResult,
    barcode_type,
    ean13_to_gtin,
    is_variable_measure,
    parse_scan_string,
    scan_to_gtin,
    strip_price_embedded,
    upc_a_to_gtin,
    validate_scan,
)


def test_barcodes_functions():
    assert upc_a_to_gtin("073621007017") == "00073621007017"
    assert ean13_to_gtin("7502264930572") == "07502264930572"
    assert barcode_type("073621007017") == "UPC-A"
    assert barcode_type("(01)07502264930572(10)LOT1") == "GS1-128"
    assert scan_to_gtin("(01)07502264930572(10)LOT1") == "07502264930572"
    res = parse_scan_string("073621007017")
    assert isinstance(res, ScanResult) and res.symbology == "UPC-A"
    assert validate_scan("07502264930572") is True
    assert is_variable_measure("00212345059994") is True
    stripped = strip_price_embedded("00212345059994")
    assert stripped.startswith("0021234500000")
    assert validate_scan(stripped) is True
