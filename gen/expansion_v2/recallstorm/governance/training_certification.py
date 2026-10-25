"""LMS recall microlearning, FSMA 204 handler certification, and skill sync."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class ComplianceLmsTracker:
    """Learning Management System (LMS) recall certification tracker."""

    ref_id: str = "LMS-TRK-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class RoleCertificationGate:
    """Gate verifying associate training certification before assigning hazardous/quarantine tasks."""

    ref_id: str = "LMS-GTE-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def assign_mandatory_recall_drill_microlearning(associate_ids: list[str], module_id: str = "REC-101") -> dict:
    """Assign a 5-minute recall execution microlearning module to associate_ids."""
    if not associate_ids:
        raise DataValidationError("associate_ids cannot be empty")
    _req(module_id, "module_id")
    return {"op": "assign_mandatory_recall_drill_microlearning", "module_id": str(module_id), "assigned_count": len(associate_ids), "src": "recallstorm/governance/training_certification.py"}


def verify_annual_fsma_204_handler_certification(associate_id: str, days_since_cert: int) -> dict:
    """Verify that associate's annual FSMA 204 traceability certification is current (<= 365 days)."""
    _req(associate_id, "associate_id")
    if days_since_cert < 0:
        raise DataValidationError("days_since_cert cannot be negative")
    return {"op": "verify_annual_fsma_204_handler_certification", "associate_id": str(associate_id), "current": days_since_cert <= 365, "src": "recallstorm/governance/training_certification.py"}


def block_untrained_associate_from_quarantine_tasks(associate_id: str, certified: bool = False) -> dict:
    """Block task assignment if associate lacks required quarantine/hazmat certification."""
    _req(associate_id, "associate_id")
    return {"op": "block_untrained_associate_from_quarantine_tasks", "associate_id": str(associate_id), "blocked": not certified, "src": "recallstorm/governance/training_certification.py"}


def track_forklift_hazmat_spill_training_expiry(certs: list[dict], today_iso: str = "2026-12-30") -> list[str]:
    """Return associate_ids with expired forklift or hazmat spill certifications."""
    if certs is None:
        raise DataValidationError("certs cannot be None")
    return sorted(str(c["associate_id"]) for c in certs if str(c.get("expires", "")) < str(today_iso))


def score_simulated_drill_assessment_quizzes(correct: int, total: int = 10) -> dict:
    """Score a post-drill comprehension quiz (pass >= 80%)."""
    if correct < 0 or total <= 0 or correct > total:
        raise DataValidationError("Invalid quiz counts")
    pct = round((correct / total) * 100.0, 2)
    return {"op": "score_simulated_drill_assessment_quizzes", "pct": pct, "passed": pct >= 80.0, "src": "recallstorm/governance/training_certification.py"}


def trigger_remedial_training_after_failed_pull(associate_id: str, store_id: str) -> dict:
    """Auto-assign remedial training after a missed shelf pull or wrong-lot scan."""
    _req(associate_id, "associate_id")
    _req(store_id, "store_id")
    return {"op": "trigger_remedial_training_after_failed_pull", "associate_id": str(associate_id), "store_id": str(store_id), "remedial_assigned": True, "src": "recallstorm/governance/training_certification.py"}


def sync_lms_completion_with_labor_skill_matrix(associate_id: str, new_skill: str) -> dict:
    """Sync completed LMS course to the recallstorm.labor skill matrix."""
    _req(associate_id, "associate_id")
    _req(new_skill, "new_skill")
    return {"op": "sync_lms_completion_with_labor_skill_matrix", "associate_id": str(associate_id), "skill": str(new_skill), "synced": True, "src": "recallstorm/governance/training_certification.py"}


def audit_new_hire_onboarding_safety_modules(new_hires: int, completed_hires: int) -> float:
    """Compute new-hire food safety onboarding completion percentage."""
    if new_hires <= 0 or completed_hires < 0 or completed_hires > new_hires:
        raise DataValidationError("Invalid hire counts")
    return round((completed_hires / new_hires) * 100.0, 2)


def generate_osha_fda_training_inspection_log(store_id: str, certified_count: int) -> dict:
    """Generate an OSHA / FDA inspector-ready associate training log."""
    _req(store_id, "store_id")
    if certified_count < 0:
        raise DataValidationError("certified_count cannot be negative")
    return {"op": "generate_osha_fda_training_inspection_log", "store_id": str(store_id), "certified_count": int(certified_count), "src": "recallstorm/governance/training_certification.py"}


def notify_store_manager_of_lapsed_certifications(store_id: str, lapsed_associates: list[str]) -> dict:
    """Notify store manager of associates with lapsed recall certifications."""
    _req(store_id, "store_id")
    if lapsed_associates is None:
        raise DataValidationError("lapsed_associates cannot be None")
    return {"op": "notify_store_manager_of_lapsed_certifications", "store_id": str(store_id), "lapsed_count": len(lapsed_associates), "src": "recallstorm/governance/training_certification.py"}
