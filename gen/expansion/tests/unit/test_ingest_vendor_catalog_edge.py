"""Edge tests for recallstorm.ingest.vendor_catalog."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.ingest.vendor_catalog import (
    parse_vendor_row,
    vendor_reformulation_date,
)


def test_vendor_edge():
    with pytest.raises(DataValidationError):
        parse_vendor_row({"sku_id": "S1"})
    assert vendor_reformulation_date({}) is None
    with pytest.raises(ValueError):
        vendor_reformulation_date({"reformulation_date": "not-a-date"})
