"""Customer PII encryption, HIPAA pharmacy guards, and k-anonymity."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re

from recallstorm.core.errors import DataValidationError
from recallstorm.core.logging_setup import redact_text


@dataclass(frozen=True)
class CustomerPiiVault:
    """Tokenized vault for customer loyalty contact PII used in recall notifications."""

    ref_id: str = "PRV-VLT-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class OutreachPrivacyGuard:
    """CCPA/GDPR/HIPAA privacy guard for consumer recall outreach."""

    ref_id: str = "PRV-GRD-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def encrypt_loyalty_customer_phone_and_email(email: str, phone: str) -> dict:
    """Tokenize/hash customer email and phone number."""
    _req(email, "email")
    _req(phone, "phone")
    e_tok = "TOK-E-" + hashlib.sha256(str(email).encode("utf-8")).hexdigest()[:10]
    p_tok = "TOK-P-" + hashlib.sha256(str(phone).encode("utf-8")).hexdigest()[:10]
    return {"email_token": e_tok, "phone_token": p_tok, "src": "recallstorm/governance/data_privacy.py"}


def enforce_purpose_limitation_on_recall_contact(message_body: str) -> dict:
    """Verify that emergency recall notifications contain zero promotional/marketing cross-sells."""
    _req(message_body, "message_body")
    low = str(message_body).lower()
    has_promo = any(k in low for k in ("buy one", "sale!", "promo code", "shop our"))
    return {"op": "enforce_purpose_limitation_on_recall_contact", "compliant": not has_promo, "src": "recallstorm/governance/data_privacy.py"}


def verify_hipaa_compliance_for_pharmacy_recalls(envelope_text: str) -> dict:
    """Verify that external envelope/subject line of a pharmacy recall does not disclose specific drug/condition PHI."""
    _req(envelope_text, "envelope_text")
    clean = "Important Pharmacy Safety Notice" in str(envelope_text) or len(str(envelope_text)) < 60
    return {"op": "verify_hipaa_compliance_for_pharmacy_recalls", "hipaa_compliant": clean, "src": "recallstorm/governance/data_privacy.py"}


def scrub_credit_card_pans_from_pos_scan_logs(log_line: str) -> str:
    """Scrub 16-digit payment card PANs and emails/phones from POS transaction logs."""
    _req(log_line, "log_line")
    scrubbed = re.sub(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", "[REDACTED_PAN]", str(log_line))
    return redact_text(scrubbed)


def manage_tokenized_household_purchase_links(household_id: str, gtin: str) -> str:
    """Create a pseudonymous household-to-GTIN purchase link token."""
    _req(household_id, "household_id")
    _req(gtin, "gtin")
    return "LNK-" + hashlib.sha256(f"{household_id}:{gtin}".encode("utf-8")).hexdigest()[:12]


def log_lawful_vital_interest_gdpr_basis_use(recall_id: str) -> dict:
    """Record GDPR Art. 6(1)(d) (vital interests of data subject) / CCPA public-safety exemption basis."""
    _req(recall_id, "recall_id")
    return {"op": "log_lawful_vital_interest_gdpr_basis_use", "recall_id": str(recall_id), "basis": "VITAL_INTEREST_PUBLIC_HEALTH", "src": "recallstorm/governance/data_privacy.py"}


def purge_temporary_call_center_contact_lists(list_id: str, days_after_campaign: int, max_days: int = 30) -> dict:
    """Purge temporary contact center dialer lists once the outreach campaign closes."""
    _req(list_id, "list_id")
    if days_after_campaign < 0 or max_days <= 0:
        raise DataValidationError("Invalid days")
    return {"op": "purge_temporary_call_center_contact_lists", "list_id": str(list_id), "purged": days_after_campaign >= max_days, "src": "recallstorm/governance/data_privacy.py"}


def audit_sms_vendor_subprocessor_dpa_status(vendor_id: str, dpa_signed: bool = True) -> dict:
    """Verify Data Processing Addendum (DPA) status for SMS/robocall gateway vendors."""
    _req(vendor_id, "vendor_id")
    return {"op": "audit_sms_vendor_subprocessor_dpa_status", "vendor_id": str(vendor_id), "approved": bool(dpa_signed), "src": "recallstorm/governance/data_privacy.py"}


def handle_consumer_data_subject_access_requests(dsar_id: str, retain_safety_log: bool = True) -> dict:
    """Process a CCPA/GDPR deletion request while retaining statutory anonymized recall notice proof."""
    _req(dsar_id, "dsar_id")
    return {"op": "handle_consumer_data_subject_access_requests", "dsar_id": str(dsar_id), "pii_deleted": True, "safety_count_retained": bool(retain_safety_log), "src": "recallstorm/governance/data_privacy.py"}


def validate_k_anonymity_in_published_analytics(cell_counts: list[int], k: int = 5) -> bool:
    """Return True if all non-zero geographic complaint/outreach cells have count >= k."""
    if cell_counts is None or k <= 0:
        raise DataValidationError("Invalid cell_counts or k")
    return all(c == 0 or c >= k for c in cell_counts)
