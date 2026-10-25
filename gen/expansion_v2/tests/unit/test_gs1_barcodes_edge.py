"""Edge case tests for recallstorm.gs1.barcodes."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.gs1.barcodes import barcode_type, scan_to_gtin, validate_scan


def test_barcodes_edge():
    assert barcode_type("123") == "UNKNOWN"
    assert validate_scan("123") is False
    with pytest.raises(DataValidationError):
        scan_to_gtin("INVALID")
