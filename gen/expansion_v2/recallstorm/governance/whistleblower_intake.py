"""Anonymous safety tip intake, zero-knowledge protection, and QA triage."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class EthicsHotlineIntake:
    """Intake portal for anonymous food-safety and recall-bypass tips."""

    ref_id: str = "ETH-INT-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class AnonymousSafetyReport:
    """Anonymized employee food safety report."""

    ref_id: str = "ETH-RPT-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def ingest_anonymous_backroom_bypass_tips(store_id: str, allegation: str) -> dict:
    """Ingest an anonymous hotline tip alleging unpulled recalled stock or falsified sign-off."""
    _req(store_id, "store_id")
    _req(allegation, "allegation")
    return {"op": "ingest_anonymous_backroom_bypass_tips", "store_id": str(store_id), "allegation": str(allegation), "src": "recallstorm/governance/whistleblower_intake.py"}


def protect_reporter_identity_via_zero_knowledge(passphrase: str) -> str:
    """Generate a one-way anonymous follow-up token without storing reporter identity."""
    _req(passphrase, "passphrase")
    return "ANON-" + hashlib.sha256(str(passphrase).encode("utf-8")).hexdigest()[:12]


def route_deliberate_relabeling_allegations_to_lp(tip_id: str, store_id: str) -> dict:
    """Immediately route allegations of date-code tampering or relabeling to Ethics & Asset Protection."""
    _req(tip_id, "tip_id")
    _req(store_id, "store_id")
    return {"op": "route_deliberate_relabeling_allegations_to_lp", "tip_id": str(tip_id), "store_id": str(store_id), "priority": "IMMEDIATE_INVESTIGATION", "src": "recallstorm/governance/whistleblower_intake.py"}


def triage_pest_or_temperature_cover_up_claims(allegation: str) -> str:
    """Classify hotline claim into 'PEST_CONTROL', 'COLD_CHAIN', 'RECALL_BYPASS', or 'GENERAL_QA'."""
    _req(allegation, "allegation")
    low = str(allegation).lower()
    if "rodent" in low or "mouse" in low or "pest" in low:
        return "PEST_CONTROL"
    if "cooler" in low or "freezer" in low or "warm" in low or "temp" in low:
        return "COLD_CHAIN"
    if "recall" in low or "pull" in low:
        return "RECALL_BYPASS"
    return "GENERAL_QA"


def enforce_non_retaliation_monitoring_flags(store_id: str) -> dict:
    """Activate FSMA Section 402 whistleblower non-retaliation HR monitoring flag on store_id."""
    _req(store_id, "store_id")
    return {"op": "enforce_non_retaliation_monitoring_flags", "store_id": str(store_id), "fsma_402_protected": True, "src": "recallstorm/governance/whistleblower_intake.py"}


def link_tip_to_specific_store_and_lot_audit(tip_id: str, store_id: str, sku_id: str) -> dict:
    """Link an ethics tip to an unannounced store shelf and backroom audit."""
    _req(tip_id, "tip_id")
    _req(store_id, "store_id")
    _req(sku_id, "sku_id")
    return {"op": "link_tip_to_specific_store_and_lot_audit", "tip_id": str(tip_id), "store_id": str(store_id), "sku_id": str(sku_id), "src": "recallstorm/governance/whistleblower_intake.py"}


def track_internal_investigation_sla_milestones(hours_elapsed: float, sla_hours: float = 24.0) -> dict:
    """Track investigation triage against 24-hour food safety SLA."""
    if hours_elapsed < 0 or sla_hours <= 0:
        raise DataValidationError("Invalid hours")
    return {"op": "track_internal_investigation_sla_milestones", "within_sla": hours_elapsed <= sla_hours, "src": "recallstorm/governance/whistleblower_intake.py"}


def require_independent_qa_verification_visit(store_id: str, home_district_mgr_excluded: bool = True) -> dict:
    """Require an independent corporate QA specialist (outside the store's reporting chain) to verify the tip."""
    _req(store_id, "store_id")
    return {"op": "require_independent_qa_verification_visit", "store_id": str(store_id), "independent": bool(home_district_mgr_excluded), "src": "recallstorm/governance/whistleblower_intake.py"}


def document_substantiated_finding_remediation(tip_id: str, substantiated: bool, corrective_action: str) -> dict:
    """Document investigation findings and CAPA remediation."""
    _req(tip_id, "tip_id")
    _req(corrective_action, "corrective_action")
    return {"op": "document_substantiated_finding_remediation", "tip_id": str(tip_id), "substantiated": bool(substantiated), "action": str(corrective_action), "src": "recallstorm/governance/whistleblower_intake.py"}


def generate_audit_committee_ethics_summary(total_tips: int, substantiated_count: int) -> dict:
    """Generate Board Audit Committee summary of food-safety hotline reports."""
    if total_tips < 0 or substantiated_count < 0 or substantiated_count > total_tips:
        raise DataValidationError("Invalid tip counts")
    return {"op": "generate_audit_committee_ethics_summary", "total_tips": int(total_tips), "substantiated_count": int(substantiated_count), "src": "recallstorm/governance/whistleblower_intake.py"}
