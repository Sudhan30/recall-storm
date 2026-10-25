"""Can seam integrity, FDA reconditioning protocols, and relabeling."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class ReconditioningProtocol:
    """FDA Compliance Policy Guide reconditioning/relabeling protocol."""

    ref_id: str = "SALV-REC-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class SalvageEligibilityEngine:
    """Engine determining whether held goods can be reconditioned or must be destroyed."""

    ref_id: str = "SALV-ELG-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def evaluate_dented_can_seam_integrity(double_seam_dent: bool, swelled_end: bool = False) -> dict:
    """Evaluate metal can defects (double-seam dents or swelled ends must be rejected/destroyed)."""
    reject = bool(double_seam_dent or swelled_end)
    return {"op": "evaluate_dented_can_seam_integrity", "reject": reject, "salvageable": not reject, "src": "recallstorm/food_safety/salvage_reconditioning.py"}


def check_smoke_water_damage_exposure(packaging_type: str, flood_water_contact: bool = False) -> dict:
    """Evaluate fire smoke or flood water exposure (any flood water contact requires destruction)."""
    _req(packaging_type, "packaging_type")
    destroy = bool(flood_water_contact) or str(packaging_type).lower() in {"paper", "cardboard", "screw_top"}
    return {"op": "check_smoke_water_damage_exposure", "destroy_mandatory": destroy, "src": "recallstorm/food_safety/salvage_reconditioning.py"}


def apply_fda_reconditioning_guidelines(reason_class: str) -> dict:
    """Determine if a recall reason class is eligible for relabeling/reconditioning."""
    _req(reason_class, "reason_class")
    rc = str(reason_class).upper()
    eligible = rc in {"MISBRANDING", "LABEL_OMISSION"}
    return {"op": "apply_fda_reconditioning_guidelines", "reason_class": rc, "eligible": eligible, "src": "recallstorm/food_safety/salvage_reconditioning.py"}


def calculate_rework_labor_viability(rework_cost_usd: float, product_value_usd: float) -> dict:
    """Check whether reconditioning cost is economically viable (< 60% of product value)."""
    if rework_cost_usd < 0 or product_value_usd <= 0:
        raise DataValidationError("Invalid cost or value")
    viable = rework_cost_usd <= (product_value_usd * 0.6)
    return {"op": "calculate_rework_labor_viability", "viable": viable, "src": "recallstorm/food_safety/salvage_reconditioning.py"}


def track_relabeling_allergen_stickers(batch_id: str, stickers_applied: int) -> dict:
    """Track corrective over-sticker application and reconciliation."""
    _req(batch_id, "batch_id")
    if stickers_applied < 0:
        raise DataValidationError("stickers_applied cannot be negative")
    return {"op": "track_relabeling_allergen_stickers", "batch_id": str(batch_id), "stickers_applied": int(stickers_applied), "src": "recallstorm/food_safety/salvage_reconditioning.py"}


def verify_state_inspector_supervision(rework_id: str, inspector_present: bool = True) -> dict:
    """Verify FDA/State inspector supervision during reconditioning."""
    _req(rework_id, "rework_id")
    return {"op": "verify_state_inspector_supervision", "rework_id": str(rework_id), "supervised": bool(inspector_present), "src": "recallstorm/food_safety/salvage_reconditioning.py"}


def segregate_non_salvageable_leakers(total_cases: int, leaker_cases: int) -> dict:
    """Separate leaking/damaged cases from intact cases."""
    if total_cases < 0 or leaker_cases < 0 or leaker_cases > total_cases:
        raise DataValidationError("Invalid case counts")
    return {"op": "segregate_non_salvageable_leakers", "intact_cases": total_cases - leaker_cases, "leaker_cases": leaker_cases, "src": "recallstorm/food_safety/salvage_reconditioning.py"}


def audit_salvage_broker_credentials(broker_id: str, licensed: bool = True) -> dict:
    """Audit state food salvage dealer license."""
    _req(broker_id, "broker_id")
    return {"op": "audit_salvage_broker_credentials", "broker_id": str(broker_id), "approved": bool(licensed), "src": "recallstorm/food_safety/salvage_reconditioning.py"}


def generate_reconditioned_lot_code(orig_lot: str) -> str:
    """Generate a traceable reconditioned lot code suffix."""
    _req(orig_lot, "orig_lot")
    return f"{str(orig_lot).strip().upper()}-RECOND"


def record_rework_yield_shrinkage(input_units: int, output_units: int) -> dict:
    """Record unit shrinkage during reconditioning/rework."""
    if input_units <= 0 or output_units < 0 or output_units > input_units:
        raise DataValidationError("Invalid input/output units")
    lost = input_units - output_units
    return {"op": "record_rework_yield_shrinkage", "lost_units": lost, "yield_pct": round((output_units / input_units) * 100.0, 2), "src": "recallstorm/food_safety/salvage_reconditioning.py"}
