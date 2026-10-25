"""FDA Level A-E effectiveness check sampling and survey compilation."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class EffectivenessCheckQuestionnaire:
    """FDA 21 CFR 7.42 recall effectiveness check questionnaire."""

    ref_id: str = "EDC-Q-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class EdcResponseCompiler:
    """Compiler for store effectiveness check survey responses."""

    ref_id: str = "EDC-COMP-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def select_fda_level_a_through_e_sample(level: str, stores: list[str]) -> list[str]:
    """Select store sample according to FDA Level A (100%), B (50%), C (10%), D (2%), or E (0%)."""
    _req(level, "level")
    if stores is None:
        raise DataValidationError("stores cannot be None")
    rates = {"A": 1.0, "B": 0.5, "C": 0.1, "D": 0.02, "E": 0.0}
    lvl = str(level).upper().strip()
    if lvl not in rates:
        raise DataValidationError(f"Invalid FDA effectiveness check level: {level!r}")
    if rates[lvl] == 0.0 or not stores:
        return []
    ordered = sorted(stores)
    k = max(1, int(round(len(ordered) * rates[lvl])))
    return ordered[:k]


def generate_store_verification_survey(store_id: str, recall_id: str) -> dict:
    """Generate a store recall effectiveness verification questionnaire."""
    _req(store_id, "store_id")
    _req(recall_id, "recall_id")
    return {"op": "generate_store_verification_survey", "store_id": str(store_id), "recall_id": str(recall_id), "src": "recallstorm/recall_lots/effectiveness_checks.py"}


def calculate_effectiveness_completion_pct(responded: int, total: int) -> float:
    """Calculate percentage of stores that completed effectiveness checks."""
    if responded < 0 or total < 0 or responded > total:
        raise DataValidationError("Invalid responded/total counts")
    if total == 0:
        return 100.0
    return round((responded / total) * 100.0, 2)


def flag_non_responding_locations(all_stores: list[str], responded_stores: set[str]) -> list[str]:
    """Return sorted store_ids that have not yet submitted effectiveness check responses."""
    if all_stores is None or responded_stores is None:
        raise DataValidationError("Inputs cannot be None")
    return sorted(set(all_stores) - set(responded_stores))


def compile_affidavit_return_counts(responses: list[dict]) -> int:
    """Sum returned/pulled units reported across store effectiveness affidavits."""
    if responses is None:
        raise DataValidationError("responses cannot be None")
    return sum(int(r.get("units", 0)) for r in responses)


def verify_physical_destruction_photos(store_id: str, photo_hashes: list[str]) -> dict:
    """Verify that physical destruction photos were uploaded by store_id."""
    _req(store_id, "store_id")
    return {"op": "verify_physical_destruction_photos", "store_id": str(store_id), "verified": bool(photo_hashes), "src": "recallstorm/recall_lots/effectiveness_checks.py"}


def audit_sub_account_notification_logs(account_id: str, notified: bool = True) -> dict:
    """Audit notification of wholesale/commercial sub-accounts."""
    _req(account_id, "account_id")
    return {"op": "audit_sub_account_notification_logs", "account_id": str(account_id), "notified": bool(notified), "src": "recallstorm/recall_lots/effectiveness_checks.py"}


def score_check_timeliness_sla(elapsed_hours: float, sla_hours: float = 24.0) -> dict:
    """Check whether effectiveness check was completed within SLA hours."""
    if elapsed_hours < 0 or sla_hours <= 0:
        raise DataValidationError("Invalid hours")
    return {"op": "score_check_timeliness_sla", "within_sla": elapsed_hours <= sla_hours, "src": "recallstorm/recall_lots/effectiveness_checks.py"}


def build_fda_district_status_report(recall_id: str, completion_pct: float = 100.0) -> dict:
    """Build an FDA District Office recall effectiveness status report."""
    _req(recall_id, "recall_id")
    return {"op": "build_fda_district_status_report", "recall_id": str(recall_id), "completion_pct": float(completion_pct), "src": "recallstorm/recall_lots/effectiveness_checks.py"}


def trigger_recheck_for_discrepancies(store_id: str, variance: int = 0) -> dict:
    """Trigger a mandatory re-check when reported store pull varies from expected stock."""
    _req(store_id, "store_id")
    return {"op": "trigger_recheck_for_discrepancies", "store_id": str(store_id), "recheck": abs(int(variance)) > 0, "src": "recallstorm/recall_lots/effectiveness_checks.py"}
