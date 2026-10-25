"""Unit tests for recallstorm.comms.media_holding_statements."""
from recallstorm.comms.media_holding_statements import (
    PrCrisisStatement,
    SocialMediaMonitor,
    align_statement_with_fda_release_time,
    approve_corporate_website_recall_page,
    archive_public_relations_timeline,
    brief_executive_spokesperson_q_and_a,
    coordinate_trade_association_alignment,
    draft_reactive_media_holding_statement,
    flag_viral_tiktok_product_complaints,
    monitor_local_news_social_mentions,
    track_journalist_inquiry_deadlines,
    verify_store_no_comment_policy_reminder,
)


def test_media_holding_statements():
    assert PrCrisisStatement().status == "ACTIVE"
    assert SocialMediaMonitor().status == "ACTIVE"
    assert "Customer safety" in draft_reactive_media_holding_statement("R1", "Sprinkles")
    assert monitor_local_news_social_mentions(30, 25)["alert"] is True
    assert flag_viral_tiktok_product_complaints("VID1", 50000)["viral_alert"] is True
    assert coordinate_trade_association_alignment("FMI", "R1")["assoc_name"] == "FMI"
    assert approve_corporate_website_recall_page("R1", True)["live"] is True
    assert track_journalist_inquiry_deadlines("AP", 30.0)["urgent"] is True
    assert align_statement_with_fda_release_time("2026-12-30T12:00", "2026-12-30T11:00")["aligned"] is True
    assert brief_executive_spokesperson_q_and_a("R1", ["POS locked"])["fact_count"] == 1
    assert verify_store_no_comment_policy_reminder("WM1")["reminded"] is True
    assert archive_public_relations_timeline("R1", 4)["events_count"] == 4
