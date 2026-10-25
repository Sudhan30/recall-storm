"""Unit tests for recallstorm.recall_lots.depth_of_recall."""
from recallstorm.recall_lots.depth_of_recall import (
    DepthPolicyEngine,
    RecallDepthLevel,
    assign_public_placard_requirement,
    check_institutional_foodservice_scope,
    configure_customer_outreach_tier,
    determine_consumer_vs_retail_depth,
    escalate_class_i_depth_rules,
    evaluate_wholesale_only_quarantine,
    generate_depth_execution_matrix,
    map_depth_to_labor_urgency,
    trigger_point_of_sale_lockout,
    validate_depth_against_fda_class,
)


def test_depth_of_recall():
    assert RecallDepthLevel().status == "ACTIVE"
    assert DepthPolicyEngine().status == "ACTIVE"
    assert determine_consumer_vs_retail_depth("Class I") == "CONSUMER"
    assert determine_consumer_vs_retail_depth("Class II") == "RETAIL"
    assert determine_consumer_vs_retail_depth("Class III") == "WHOLESALE"
    assert evaluate_wholesale_only_quarantine("WHOLESALE")["dc_only"] is True
    assert trigger_point_of_sale_lockout("RETAIL")["pos_lock"] is True
    assert assign_public_placard_requirement("CONSUMER")["placard_required"] is True
    assert configure_customer_outreach_tier("CONSUMER") == "ROBOCALL_SMS_EMAIL"
    assert check_institutional_foodservice_scope("RETAIL")["included"] is True
    assert escalate_class_i_depth_rules("Class I")["sla_hours"] == 2
    assert map_depth_to_labor_urgency("CONSUMER") == 1
    assert validate_depth_against_fda_class("CONSUMER", "Class I") is True
    assert generate_depth_execution_matrix("Class I")["depth"] == "CONSUMER"
