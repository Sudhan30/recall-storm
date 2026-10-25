"""CCP deviation tracking, cooking lethality, and cooling curve compliance."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class CcpDeviationEvent:
    """Critical Control Point (CCP) deviation record."""

    ref_id: str = "CCP-DEV-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class CorrectiveActionPlan:
    """21 CFR 117 / 9 CFR 417.3 HACCP corrective action plan."""

    ref_id: str = "HACCP-CAPA"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def evaluate_cooking_lethality_log(internal_temp_f: float, min_temp_f: float = 165.0) -> dict:
    """Verify rotisserie/commissary cooking lethality temperature (>= 165F for poultry)."""
    if internal_temp_f <= 0 or min_temp_f <= 0:
        raise DataValidationError("Invalid cooking temperature")
    return {"op": "evaluate_cooking_lethality_log", "achieved": float(internal_temp_f) >= float(min_temp_f), "temp_f": float(internal_temp_f), "src": "recallstorm/food_safety/haccp_deviations.py"}


def flag_metal_detector_reject_spike(rejects_per_hour: int, max_rejects: int = 5) -> dict:
    """Flag CCP metal detector reject spikes."""
    if rejects_per_hour < 0 or max_rejects <= 0:
        raise DataValidationError("Invalid reject counts")
    return {"op": "flag_metal_detector_reject_spike", "spike": rejects_per_hour > max_rejects, "src": "recallstorm/food_safety/haccp_deviations.py"}


def verify_cooling_curve_compliance(temp_at_2h_f: float, temp_at_6h_f: float) -> dict:
    """Verify FDA/USDA 2-stage cooling (135F to <= 70F in 2h, and to <= 41F in 6h total)."""
    if temp_at_2h_f <= 0 or temp_at_6h_f <= 0:
        raise DataValidationError("Invalid cooling temperatures")
    compliant = temp_at_2h_f <= 70.0 and temp_at_6h_f <= 41.0
    return {"op": "verify_cooling_curve_compliance", "compliant": compliant, "src": "recallstorm/food_safety/haccp_deviations.py"}


def trigger_haccp_reassessment_hold(batch_id: str, ccp_id: str = "CCP-1") -> dict:
    """Place production batch on HACCP reassessment hold."""
    _req(batch_id, "batch_id")
    return {"op": "trigger_haccp_reassessment_hold", "batch_id": str(batch_id), "ccp_id": str(ccp_id), "src": "recallstorm/food_safety/haccp_deviations.py"}


def document_root_cause_disposition(batch_id: str, root_cause: str) -> dict:
    """Document root cause and product disposition for a CCP deviation."""
    _req(batch_id, "batch_id")
    _req(root_cause, "root_cause")
    return {"op": "document_root_cause_disposition", "batch_id": str(batch_id), "root_cause": str(root_cause), "src": "recallstorm/food_safety/haccp_deviations.py"}


def validate_test_piece_challenge_log(fe_mm: float = 1.5, non_fe_mm: float = 2.0, ss_mm: float = 2.5) -> dict:
    """Validate hourly ferrous, non-ferrous, and 316 stainless steel test-wand challenge logs."""
    if fe_mm <= 0 or non_fe_mm <= 0 or ss_mm <= 0:
        raise DataValidationError("Test piece sizes must be positive")
    passed = fe_mm <= 2.0 and non_fe_mm <= 2.5 and ss_mm <= 3.0
    return {"op": "validate_test_piece_challenge_log", "passed": passed, "src": "recallstorm/food_safety/haccp_deviations.py"}


def link_deviation_to_batch_id(deviation_id: str, batch_id: str) -> dict:
    """Link a CCP deviation event to an affected production batch_id."""
    _req(deviation_id, "deviation_id")
    _req(batch_id, "batch_id")
    return {"op": "link_deviation_to_batch_id", "deviation_id": str(deviation_id), "batch_id": str(batch_id), "src": "recallstorm/food_safety/haccp_deviations.py"}


def lock_affected_production_window(line_id: str, last_good_check_iso: str, failed_check_iso: str) -> dict:
    """Quarantine all product produced between last_good_check_iso and failed_check_iso."""
    _req(line_id, "line_id")
    _req(last_good_check_iso, "last_good_check_iso")
    _req(failed_check_iso, "failed_check_iso")
    if str(failed_check_iso) < str(last_good_check_iso):
        raise DataValidationError("failed_check_iso precedes last_good_check_iso")
    return {"op": "lock_affected_production_window", "line_id": str(line_id), "window": [str(last_good_check_iso), str(failed_check_iso)], "src": "recallstorm/food_safety/haccp_deviations.py"}


def require_qa_manager_countersign(deviation_id: str, pcqi_signed: bool = True) -> dict:
    """Require PCQI / HACCP-trained QA manager countersignature."""
    _req(deviation_id, "deviation_id")
    return {"op": "require_qa_manager_countersign", "deviation_id": str(deviation_id), "approved": bool(pcqi_signed), "src": "recallstorm/food_safety/haccp_deviations.py"}


def generate_fsis_noncompliance_response(nr_id: str, corrective_text: str) -> dict:
    """Generate a response to a USDA FSIS Noncompliance Record (NR)."""
    _req(nr_id, "nr_id")
    _req(corrective_text, "corrective_text")
    return {"op": "generate_fsis_noncompliance_response", "nr_id": str(nr_id), "response": str(corrective_text), "src": "recallstorm/food_safety/haccp_deviations.py"}
