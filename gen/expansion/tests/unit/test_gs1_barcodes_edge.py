"""Edge tests for recallstorm.gs1.barcodes."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.gs1.barcodes import (
    barcode_type,
    scan_to_gtin,
    validate_scan,
)


def test_barcodes_edge():
    assert validate_scan("invalid") is False
    with pytest.raises(DataValidationError):
        barcode_type("")
    with pytest.raises(DataValidationError):
        barcode_type("12345")
    with pytest.raises(DataValidationError):
        scan_to_gtin("")
