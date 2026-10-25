"""FDA district recall status filings and inspector visit binders."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError
from recallstorm.core.logging_setup import redact_text


@dataclass(frozen=True)
class RegulatoryStatusFiling:
    """21 CFR 7.53 periodic recall status report for FDA District Office."""

    ref_id: str = "REG-FIL-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class InspectorVisitPacket:
    """In-store compliance binder for visiting FDA/State inspectors."""

    ref_id: str = "REG-PCK-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def compile_fda_district_recall_status_report(recall_id: str, stores_completed: int, total_stores: int) -> dict:
    """Compile a 21 CFR 7.53 recall status report for the FDA Recall Coordinator."""
    _req(recall_id, "recall_id")
    if stores_completed < 0 or total_stores <= 0 or stores_completed > total_stores:
        raise DataValidationError("Invalid store completion counts")
    return {"op": "compile_fda_district_recall_status_report", "recall_id": str(recall_id), "pct": round((stores_completed / total_stores) * 100.0, 2), "src": "recallstorm/comms/regulator_reports.py"}


def format_state_dept_of_ag_store_list(state: str, store_ids: list[str]) -> dict:
    """Format state-specific store list for State Dept of Agriculture / Health."""
    _req(state, "state")
    if store_ids is None:
        raise DataValidationError("store_ids cannot be None")
    return {"op": "format_state_dept_of_ag_store_list", "state": str(state).upper(), "stores": sorted(store_ids), "src": "recallstorm/comms/regulator_reports.py"}


def prepare_store_manager_inspector_binder(store_id: str, pull_count: int) -> dict:
    """Assemble digital/printable inspector packet for store_id."""
    _req(store_id, "store_id")
    if pull_count < 0:
        raise DataValidationError("pull_count cannot be negative")
    return {"op": "prepare_store_manager_inspector_binder", "store_id": str(store_id), "pull_count": int(pull_count), "src": "recallstorm/comms/regulator_reports.py"}


def log_regulatory_in_store_sample_receipts(store_id: str, form_fda_484_id: str) -> dict:
    """Log FDA Form 484 Receipt for Samples when an investigator collects samples in-store."""
    _req(store_id, "store_id")
    _req(form_fda_484_id, "form_fda_484_id")
    return {"op": "log_regulatory_in_store_sample_receipts", "store_id": str(store_id), "form_484": str(form_fda_484_id), "duplicate_retained": True, "src": "recallstorm/comms/regulator_reports.py"}


def track_fda_form_482_483_uploads(store_id: str, form_type: str = "FDA_482") -> dict:
    """Track upload of FDA Form 482 (Notice of Inspection) or 483 (Inspectional Observations)."""
    _req(store_id, "store_id")
    _req(form_type, "form_type")
    return {"op": "track_fda_form_482_483_uploads", "store_id": str(store_id), "form_type": str(form_type).upper(), "src": "recallstorm/comms/regulator_reports.py"}


def verify_zero_stock_attestation_accuracy(reported_zero: bool, physical_found: int = 0) -> dict:
    """Verify that a store's zero-stock attestation matches physical audit."""
    if physical_found < 0:
        raise DataValidationError("physical_found cannot be negative")
    accurate = (not reported_zero) or (physical_found == 0)
    return {"op": "verify_zero_stock_attestation_accuracy", "accurate": accurate, "src": "recallstorm/comms/regulator_reports.py"}


def redact_pii_from_submission_packages(text: str) -> str:
    """Redact consumer emails and phone numbers before external regulatory document sharing."""
    _req(text, "text")
    return redact_text(str(text))


def validate_report_against_agency_schema(report: dict) -> dict:
    """Validate that a regulatory status report dictionary has required fields."""
    if not isinstance(report, dict) or not report.get("recall_id"):
        raise DataValidationError("Regulatory report requires recall_id")
    return {"op": "validate_report_against_agency_schema", "valid": True, "src": "recallstorm/comms/regulator_reports.py"}


def manage_regulatory_inquiry_response_sla(hours_elapsed: float, sla_hours: float = 24.0) -> dict:
    """Track regulatory inquiry response time against SLA."""
    if hours_elapsed < 0 or sla_hours <= 0:
        raise DataValidationError("Invalid hours")
    return {"op": "manage_regulatory_inquiry_response_sla", "within_sla": hours_elapsed <= sla_hours, "src": "recallstorm/comms/regulator_reports.py"}


def archive_final_recall_closure_letter(recall_id: str, fda_termination_date: str) -> dict:
    """Archive official 21 CFR 7.55 FDA recall termination letter."""
    _req(recall_id, "recall_id")
    _req(fda_termination_date, "fda_termination_date")
    return {"op": "archive_final_recall_closure_letter", "recall_id": str(recall_id), "terminated_on": str(fda_termination_date), "src": "recallstorm/comms/regulator_reports.py"}
