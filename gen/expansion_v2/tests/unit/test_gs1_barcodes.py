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


def test_barcodes():
    upc = "073621007017"
    assert upc_a_to_gtin(upc) == "00073621007017"
    assert ean13_to_gtin("0073621007017") == "00073621007017"
    assert barcode_type(upc) == "UPC-A"
    assert validate_scan(upc) is True
    assert scan_to_gtin("]E0073621007017") == "00073621007017"
    sr = parse_scan_string(upc)
    assert isinstance(sr, ScanResult) and sr.gtin14 == "00073621007017"

    var_upc = "201234005995"
    assert is_variable_measure(var_upc) is True
    stripped = strip_price_embedded(var_upc)
    assert stripped.startswith("0020123400000")
    assert validate_scan(stripped) is True
