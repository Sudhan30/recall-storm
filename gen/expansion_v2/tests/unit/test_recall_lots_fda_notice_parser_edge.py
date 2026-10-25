"""Edge case tests for recallstorm.recall_lots.fda_notice_parser."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.recall_lots.fda_notice_parser import parse_fda_press_release_html, validate_parsed_notice_schema


def test_fda_notice_parser_edge():
    with pytest.raises(DataValidationError):
        parse_fda_press_release_html("")
    with pytest.raises(DataValidationError):
        validate_parsed_notice_schema({})
