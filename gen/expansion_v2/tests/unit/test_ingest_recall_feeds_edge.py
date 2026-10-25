"""Edge case tests for recallstorm.ingest.recall_feeds."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.ingest.recall_feeds import feed_cursor, feed_item_to_recall, parse_fda_rss, parse_fsis_recall


def test_recall_feeds_edge():
    with pytest.raises(DataValidationError):
        parse_fsis_recall({})
    with pytest.raises(DataValidationError):
        parse_fda_rss("")
    with pytest.raises(DataValidationError):
        parse_fda_rss("<unclosed")
    with pytest.raises(DataValidationError):
        feed_item_to_recall({})
    assert feed_cursor([]) == ""
