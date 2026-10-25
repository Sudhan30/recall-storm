"""Unit tests for recallstorm.ingest.recall_feeds."""
from recallstorm.ingest.recall_feeds import (
    RecallFeed,
    dedupe_recalls,
    feed_cursor,
    feed_item_to_recall,
    merge_recall_sources,
    parse_fda_rss,
    parse_fsis_recall,
    recall_by_state,
    recall_since,
)


def test_recall_feeds():
    fsis = parse_fsis_recall(
        {"recall_number": "FSIS-001", "title": "Beef", "recall_date": "2026-05-01", "states": "CA, NV"}
    )
    assert fsis["states"] == ["CA", "NV"]
    xml = "<rss><channel><item><guid>FDA-1</guid><title>Candy</title><pubDate>2026-06-01</pubDate></item></channel></rss>"
    fda = parse_fda_rss(xml)
    assert len(fda) == 1
    item = feed_item_to_recall({"recall_id": "FDA-2", "date": "2026-04-01", "states": ["NY"]})
    merged = merge_recall_sources([fsis], fda, [item, item])
    assert len(dedupe_recalls(merged)) == 3
    assert len(recall_since(merged, "2026-05-01")) == 2
    assert len(recall_by_state(merged, "CA")) == 2
    assert feed_cursor(merged) == "2026-06-01"
    feed = RecallFeed("MIXED", merged)
    assert len(feed.items) == 3
