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


def test_fsis_and_fda_rss():
    fsis = parse_fsis_recall(
        {
            "recall_number": "FSIS-001",
            "title": "Beef Recall",
            "recall_date": "2026-11-15",
            "states": "CA, NV",
            "summary": "Undeclared allergen",
        }
    )
    assert fsis["recall_id"] == "FSIS-001"
    assert fsis["states"] == ["CA", "NV"]

    rss_xml = """<rss><channel><item><guid>FDA-10</guid><title>Candy Recall</title><pubDate>2026-12-01</pubDate><description>Red 3</description></item></channel></rss>"""
    fda_list = parse_fda_rss(rss_xml)
    assert len(fda_list) == 1
    assert fda_list[0]["recall_id"] == "FDA-10"

    item = feed_item_to_recall({"id": "FDA-11", "title": "Syrup", "date": "2026-10-01", "states": ["TX"]})
    merged = merge_recall_sources([fsis], fda_list, [item, fsis])
    assert len(merged) == 3
    assert len(dedupe_recalls([fsis, fsis])) == 1
    assert len(recall_since(merged, "2026-11-01")) == 2
    assert len(recall_by_state(merged, "CA")) == 2
    feed = RecallFeed("MIXED", tuple(merged))
    assert len(feed.items) == 3
    assert len(feed_cursor(merged)) == 12
