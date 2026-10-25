"""Edge case tests for recallstorm.recall_lots.depth_of_recall."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.recall_lots.depth_of_recall import (
    determine_consumer_vs_retail_depth,
    validate_depth_against_fda_class,
)


def test_depth_of_recall_edge():
    assert validate_depth_against_fda_class("WHOLESALE", "Class I") is False
    with pytest.raises(DataValidationError):
        determine_consumer_vs_retail_depth("")
