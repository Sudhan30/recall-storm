"""Edge case tests for recallstorm.ingest.store_list."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.ingest.store_list import normalize_store_format, parse_store_csv, store_from_row


def test_store_list_edge():
    assert parse_store_csv("") == []
    with pytest.raises(DataValidationError):
        normalize_store_format("UNKNOWN_FORMAT")
    with pytest.raises(DataValidationError):
        store_from_row({})
