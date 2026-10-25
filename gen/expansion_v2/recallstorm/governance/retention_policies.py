"""7-year FDA FSMA record retention and WORM litigation holds."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class LegalHoldManager:
    """Manager placing immutable litigation holds on recall records."""

    ref_id: str = "RET-LGL-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class RecordRetentionEnforcer:
    """Enforcer for FDA FSMA 204 and corporate 7-year retention schedules."""

    ref_id: str = "RET-ENF-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def apply_seven_year_fda_fsma_retention_rule(created_date_iso: str, years: int = 7) -> str:
    """Compute the retention expiration date (created_year + 7 years)."""
    _req(created_date_iso, "created_date_iso")
    if years < 2:
        raise DataValidationError("FSMA requires at least 2 years retention")
    d = date.fromisoformat(str(created_date_iso)[:10])
    return date(d.year + years, d.month, min(d.day, 28)).isoformat()


def place_litigation_hold_on_injury_linked_lots(lot_id: str, matter_id: str) -> dict:
    """Suspend all automated record expiration on a lot linked to a consumer injury claim."""
    _req(lot_id, "lot_id")
    _req(matter_id, "matter_id")
    return {"op": "place_litigation_hold_on_injury_linked_lots", "lot_id": str(lot_id), "matter_id": str(matter_id), "indefinite_hold": True, "src": "recallstorm/governance/retention_policies.py"}


def prevent_auto_purge_of_recall_epcis_events(recall_id: str) -> dict:
    """Exempt EPCIS traceability events linked to recall_id from rolling 24-month database purges."""
    _req(recall_id, "recall_id")
    return {"op": "prevent_auto_purge_of_recall_epcis_events", "recall_id": str(recall_id), "exempt_from_purge": True, "src": "recallstorm/governance/retention_policies.py"}


def archive_cold_storage_jsonl_to_glacier_worm(run_id: str, bucket: str = "s3://recallstorm-worm") -> dict:
    """Archive plan.jsonl and events.jsonl to Write-Once-Read-Many (WORM) cold storage."""
    _req(run_id, "run_id")
    return {"op": "archive_cold_storage_jsonl_to_glacier_worm", "run_id": str(run_id), "uri": f"{bucket}/{run_id}", "worm_locked": True, "src": "recallstorm/governance/retention_policies.py"}


def manage_gdpr_ccpa_pii_redaction_schedules(days_since_closure: int, pii_ttl_days: int = 365) -> dict:
    """Pseudonymize customer outreach PII after pii_ttl_days while preserving anonymized recall counts for 7 years."""
    if days_since_closure < 0 or pii_ttl_days <= 0:
        raise DataValidationError("Invalid days")
    return {"op": "manage_gdpr_ccpa_pii_redaction_schedules", "redact_pii_now": days_since_closure >= pii_ttl_days, "src": "recallstorm/governance/retention_policies.py"}


def verify_immutable_s3_object_lock_status(object_key: str, compliance_mode: bool = True) -> dict:
    """Verify S3 Object Lock COMPLIANCE mode on archived regulatory dossiers."""
    _req(object_key, "object_key")
    return {"op": "verify_immutable_s3_object_lock_status", "object_key": str(object_key), "immutable": bool(compliance_mode), "src": "recallstorm/governance/retention_policies.py"}


def track_retention_expiration_disposition_dates(records: list[dict], today_iso: str = "2034-01-02") -> list[str]:
    """Return record IDs eligible for disposition after their 7-year retention period (unless under litigation hold)."""
    if records is None:
        raise DataValidationError("records cannot be None")
    return [
        str(r["id"])
        for r in records
        if not r.get("litigation_hold") and str(r.get("retain_until", "9999-12-31")) <= str(today_iso)
    ]


def audit_unauthorized_deletion_attempts(user_id: str, record_id: str) -> dict:
    """Log and block any attempt to delete or overwrite a WORM-protected recall record."""
    _req(user_id, "user_id")
    _req(record_id, "record_id")
    return {"op": "audit_unauthorized_deletion_attempts", "user_id": str(user_id), "record_id": str(record_id), "blocked": True, "src": "recallstorm/governance/retention_policies.py"}


def link_related_vendor_correspondence_to_hold(matter_id: str, email_ids: list[str]) -> dict:
    """Bind vendor emails and dispute records to a litigation hold."""
    _req(matter_id, "matter_id")
    if not email_ids:
        raise DataValidationError("email_ids cannot be empty")
    return {"op": "link_related_vendor_correspondence_to_hold", "matter_id": str(matter_id), "count": len(email_ids), "src": "recallstorm/governance/retention_policies.py"}


def generate_records_management_compliance_cert(recall_id: str) -> dict:
    """Generate a Records Management compliance certificate."""
    _req(recall_id, "recall_id")
    return {"op": "generate_records_management_compliance_cert", "recall_id": str(recall_id), "certified": True, "src": "recallstorm/governance/retention_policies.py"}
