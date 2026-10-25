"""Edge case tests for recallstorm.recall_lots.fsis_notice_parser."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.recall_lots.fsis_notice_parser import (
    parse_fsis_poultry_serial_range,
    parse_fsis_production_date_span,
)


def test_fsis_notice_parser_edge():
    with pytest.raises(DataValidationError):
        parse_fsis_production_date_span("2026-05-01", "2026-01-01")
    with pytest.raises(DataValidationError):
        parse_fsis_poultry_serial_range(20, 10)
