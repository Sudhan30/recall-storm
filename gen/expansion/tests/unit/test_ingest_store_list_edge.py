"""Edge tests for recallstorm.ingest.store_list."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.ingest.store_list import (
    geocode_zip,
    normalize_store_format,
    parse_address,
    parse_store_csv,
    store_from_row,
)


def test_store_list_edge():
    with pytest.raises(DataValidationError):
        normalize_store_format("UNKNOWN_FMT")
    with pytest.raises(DataValidationError):
        parse_address("")
    with pytest.raises(DataValidationError):
        geocode_zip("")
    with pytest.raises(DataValidationError):
        parse_store_csv("")
    with pytest.raises(DataValidationError):
        store_from_row({})
