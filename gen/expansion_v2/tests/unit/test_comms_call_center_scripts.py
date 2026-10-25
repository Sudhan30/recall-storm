"""Unit tests for recallstorm.comms.call_center_scripts."""
from recallstorm.comms.call_center_scripts import (
    ContactCenterKnowledgeBase,
    EscalationTriageTree,
    build_symptom_intake_decision_tree,
    generate_daily_sentiment_digest,
    log_media_press_inquiry_diversion,
    provide_instant_e_gift_card_issuance,
    publish_agent_recall_faq_article,
    route_adverse_event_to_nurse_line,
    sync_crm_case_tags_with_recall_id,
    track_call_volume_spike_by_recall,
    update_ivr_phone_tree_announcement,
    validate_caller_reported_lot_string,
)


def test_call_center_scripts():
    assert ContactCenterKnowledgeBase().status == "ACTIVE"
    assert EscalationTriageTree().status == "ACTIVE"
    assert publish_agent_recall_faq_article("R1", "Red 3 recall")["published"] is True
    assert len(build_symptom_intake_decision_tree("R1")["questions"]) == 3
    assert route_adverse_event_to_nurse_line("T1", True)["queue"] == "NURSE_TOXICOLOGY_LINE"
    assert provide_instant_e_gift_card_issuance("C1", 10.0)["amount_usd"] == 10.0
    assert validate_caller_reported_lot_string("L2601", ["L26*"])["affected"] is True
    assert log_media_press_inquiry_diversion("Local News")["diverted_to"] == "CORP_PR_DESK"
    assert update_ivr_phone_tree_announcement("R1", True)["active"] is True
    assert track_call_volume_spike_by_recall(150, 50)["spike"] is True
    assert sync_crm_case_tags_with_recall_id("CS1", "R1")["recall_id"] == "R1"
    assert generate_daily_sentiment_digest(100, 5)["escalations"] == 5
