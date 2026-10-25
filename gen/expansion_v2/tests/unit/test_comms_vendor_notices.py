"""Unit tests for recallstorm.comms.vendor_notices."""
from recallstorm.comms.vendor_notices import (
    SupplierRecallDirective,
    VendorComplianceDemand,
    demand_lot_distribution_manifest_csv,
    escalate_unresponsive_vendor_contacts,
    issue_formal_notice_of_quarantine,
    log_vendor_disposition_instructions,
    notify_vendor_of_pos_lock_activation,
    request_immediate_coa_and_root_cause,
    require_indemnification_hold_harmless,
    schedule_joint_crisis_bridge_call,
    track_vendor_portal_document_uploads,
    transmit_estimated_chargeback_schedule,
)


def test_vendor_notices():
    assert SupplierRecallDirective().status == "ACTIVE"
    assert VendorComplianceDemand().status == "ACTIVE"
    assert issue_formal_notice_of_quarantine("V1", ["S1"])["skus"] == ["S1"]
    assert request_immediate_coa_and_root_cause("V1", "L1", 4)["sla_hours"] == 4
    assert demand_lot_distribution_manifest_csv("V1", "R1")["recall_id"] == "R1"
    assert notify_vendor_of_pos_lock_activation("V1", "S1")["sku_id"] == "S1"
    assert transmit_estimated_chargeback_schedule("V1", 5000.0)["estimated_usd"] == 5000.0
    assert require_indemnification_hold_harmless("V1", "R1")["vendor_id"] == "V1"
    assert escalate_unresponsive_vendor_contacts("V1", 3.5)["escalated"] is True
    assert track_vendor_portal_document_uploads("V1", ["COA.pdf"])["doc_count"] == 1
    assert schedule_joint_crisis_bridge_call("V1", "2026-12-30T19:00")["vendor_id"] == "V1"
    assert log_vendor_disposition_instructions("V1", "DESTROY_AT_DC")["disposition"] == "DESTROY_AT_DC"
