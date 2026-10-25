"""Unit tests for recallstorm.governance.data_privacy."""
from recallstorm.governance.data_privacy import (
    CustomerPiiVault,
    OutreachPrivacyGuard,
    audit_sms_vendor_subprocessor_dpa_status,
    encrypt_loyalty_customer_phone_and_email,
    enforce_purpose_limitation_on_recall_contact,
    handle_consumer_data_subject_access_requests,
    log_lawful_vital_interest_gdpr_basis_use,
    manage_tokenized_household_purchase_links,
    purge_temporary_call_center_contact_lists,
    scrub_credit_card_pans_from_pos_scan_logs,
    validate_k_anonymity_in_published_analytics,
    verify_hipaa_compliance_for_pharmacy_recalls,
)


def test_data_privacy():
    assert CustomerPiiVault().status == "ACTIVE"
    assert OutreachPrivacyGuard().status == "ACTIVE"
    toks = encrypt_loyalty_customer_phone_and_email("a@b.com", "555-123-4567")
    assert toks["email_token"].startswith("TOK-E-")
    assert enforce_purpose_limitation_on_recall_contact("Safety Recall: Do not eat")["compliant"] is True
    assert verify_hipaa_compliance_for_pharmacy_recalls("Important Pharmacy Safety Notice")["hipaa_compliant"] is True
    assert "[REDACTED_PAN]" in scrub_credit_card_pans_from_pos_scan_logs("Card 4111-2222-3333-4444")
    assert manage_tokenized_household_purchase_links("H1", "07502264930572").startswith("LNK-")
    assert log_lawful_vital_interest_gdpr_basis_use("R1")["basis"] == "VITAL_INTEREST_PUBLIC_HEALTH"
    assert purge_temporary_call_center_contact_lists("L1", 40, 30)["purged"] is True
    assert audit_sms_vendor_subprocessor_dpa_status("V1", True)["approved"] is True
    assert handle_consumer_data_subject_access_requests("DSAR1", True)["pii_deleted"] is True
    assert validate_k_anonymity_in_published_analytics([0, 5, 12], 5) is True
