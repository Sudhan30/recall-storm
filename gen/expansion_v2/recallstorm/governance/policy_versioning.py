"""SOP Git versioning, rule threshold diffs, and legal sign-off."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class StandardOperatingProcedureGit:
    """Version-controlled SOP repository for recall playbooks."""

    ref_id: str = "POL-GIT-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class PolicyDiffTracker:
    """Tracker for statutory rule engine configuration diffs."""

    ref_id: str = "POL-DIF-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def version_control_recall_playbook_markdown(markdown_text: str) -> str:
    """Compute immutable SHA-256 commit digest of a recall SOP playbook."""
    _req(markdown_text, "markdown_text")
    return hashlib.sha256(str(markdown_text).encode("utf-8")).hexdigest()[:12]


def require_legal_review_on_jurisdiction_rules(rule_id: str, legal_counsel_id: str) -> dict:
    """Record Regulatory Legal Counsel sign-off before activating a new statutory rule."""
    _req(rule_id, "rule_id")
    _req(legal_counsel_id, "legal_counsel_id")
    return {"op": "require_legal_review_on_jurisdiction_rules", "rule_id": str(rule_id), "approved_by": str(legal_counsel_id), "src": "recallstorm/governance/policy_versioning.py"}


def track_effective_dates_of_state_ban_modules(rules_by_state: dict[str, str]) -> dict[str, str]:
    """Return mapping of state code -> effective ISO date."""
    if not rules_by_state:
        raise DataValidationError("rules_by_state cannot be empty")
    return {str(k).upper(): str(v) for k, v in rules_by_state.items()}


def diff_rule_engine_thresholds_between_drills(old_rules: dict[str, float], new_rules: dict[str, float]) -> dict[str, tuple[float | None, float | None]]:
    """Compute changed rule thresholds between two drill versions."""
    if old_rules is None or new_rules is None:
        raise DataValidationError("Rule dicts cannot be None")
    keys = set(old_rules) | set(new_rules)
    return {k: (old_rules.get(k), new_rules.get(k)) for k in sorted(keys) if old_rules.get(k) != new_rules.get(k)}


def bind_drill_execution_to_immutable_policy_sha(run_id: str, policy_sha: str) -> dict:
    """Bind a recall run_id to the exact policy_sha active at execution time."""
    _req(run_id, "run_id")
    _req(policy_sha, "policy_sha")
    return {"op": "bind_drill_execution_to_immutable_policy_sha", "run_id": str(run_id), "policy_sha": str(policy_sha), "src": "recallstorm/governance/policy_versioning.py"}


def manage_annual_sop_recertification_cycles(sop_id: str, months_since_review: int) -> dict:
    """Flag SOPs that have not been recertified within 12 months."""
    _req(sop_id, "sop_id")
    if months_since_review < 0:
        raise DataValidationError("months_since_review cannot be negative")
    return {"op": "manage_annual_sop_recertification_cycles", "sop_id": str(sop_id), "recert_due": months_since_review >= 12, "src": "recallstorm/governance/policy_versioning.py"}


def publish_redlined_policy_updates_to_field(sop_id: str, summary_of_changes: str) -> dict:
    """Publish redlined SOP update summary to field operations."""
    _req(sop_id, "sop_id")
    _req(summary_of_changes, "summary_of_changes")
    return {"op": "publish_redlined_policy_updates_to_field", "sop_id": str(sop_id), "summary": str(summary_of_changes), "src": "recallstorm/governance/policy_versioning.py"}


def roll_back_erroneous_rule_configuration_push(target_sha: str) -> dict:
    """Roll back rule engine configuration to a known-good target_sha."""
    _req(target_sha, "target_sha")
    return {"op": "roll_back_erroneous_rule_configuration_push", "rolled_back_to": str(target_sha), "src": "recallstorm/governance/policy_versioning.py"}


def audit_policy_exception_waiver_expirations(waivers: list[dict], today_iso: str = "2026-12-30") -> list[str]:
    """Return waiver_ids that have expired."""
    if waivers is None:
        raise DataValidationError("waivers cannot be None")
    return [str(w["waiver_id"]) for w in waivers if str(w.get("expires", "")) < str(today_iso)]


def generate_regulatory_change_management_log(changes: list[str]) -> dict:
    """Generate a regulatory change management log."""
    if changes is None:
        raise DataValidationError("changes cannot be None")
    return {"op": "generate_regulatory_change_management_log", "change_count": len(changes), "src": "recallstorm/governance/policy_versioning.py"}
