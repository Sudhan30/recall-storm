"""Edge tests for recallstorm.ingest.recall_feeds."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.ingest.recall_feeds import (
    feed_item_to_recall,
    parse_fda_rss,
    parse_fsis_recall,
    recall_by_state,
)


def test_invalid_inputs():
    with pytest.raises(DataValidationError):
        parse_fsis_recall({})
    with pytest.raises(DataValidationError):
        feed_item_to_recall({})
    with pytest.raises(DataValidationError):
        parse_fda_rss("")
    with pytest.raises(DataValidationError):
        parse_fda_rss("<unclosed")
    with pytest.raises(DataValidationError):
        recall_by_state([], "INVALID")
