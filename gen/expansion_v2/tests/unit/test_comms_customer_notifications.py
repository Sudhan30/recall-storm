"""Unit tests for recallstorm.comms.customer_notifications."""
from recallstorm.comms.customer_notifications import (
    AutomatedCustomerAlert,
    LoyaltyRecallOutreach,
    filter_online_delivery_order_histories,
    generate_app_push_notification_payload,
    generate_outreach_effectiveness_summary,
    handle_inbound_customer_reply_routing,
    log_opt_out_safety_override_justification,
    provide_self_service_lot_checker_url,
    query_loyalty_households_by_upc_window,
    send_personalized_email_sms_recall_alert,
    track_email_bounce_and_open_metrics,
    trigger_automated_robocall_for_class_i,
)


def test_customer_notifications():
    assert LoyaltyRecallOutreach().status == "ACTIVE"
    assert AutomatedCustomerAlert().status == "ACTIVE"
    assert query_loyalty_households_by_upc_window([{"household_id": "H1", "upc": "U1"}], "U1") == ["H1"]
    assert filter_online_delivery_order_histories([{"order_id": "O1", "skus": ["S1"]}], "S1") == ["O1"]
    assert send_personalized_email_sms_recall_alert("H1", "Sprinkles", "WM1")["sent"] is True
    assert trigger_automated_robocall_for_class_i(["H1", "H2"], "R1")["calls_queued"] == 2
    assert "https://" in provide_self_service_lot_checker_url("R1", "07502264930572")
    assert track_email_bounce_and_open_metrics(100, 10, 45)["open_rate"] == 0.5
    assert "PUBLIC_SAFETY" in log_opt_out_safety_override_justification("H1")["basis"]
    assert generate_app_push_notification_payload("H1", "Safety Recall")["household_id"] == "H1"
    assert handle_inbound_customer_reply_routing("My child got sick") == "ILLNESS_ESCALATION"
    assert generate_outreach_effectiveness_summary(500, 120)["notified"] == 500
