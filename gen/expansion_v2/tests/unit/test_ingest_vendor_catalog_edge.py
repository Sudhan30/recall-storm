"""Edge case tests for recallstorm.ingest.vendor_catalog."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.ingest.vendor_catalog import parse_vendor_row, vendor_case_pack


def test_vendor_catalog_edge():
    with pytest.raises(DataValidationError):
        parse_vendor_row({"sku_id": "V1"})
    with pytest.raises(DataValidationError):
        vendor_case_pack({"case_units": 0})
