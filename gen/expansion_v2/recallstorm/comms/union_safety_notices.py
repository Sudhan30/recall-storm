"""UFCW steward hazmat notifications, PPE rules, and SDS distribution."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class LaborUnionSafetyBrief:
    """Joint labor-management safety briefing for recall execution."""

    ref_id: str = "UNI-SAF-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class HazmatHandlingNotice:
    """OSHA HazCom / PPE handling notice for chemical or leaking recalls."""

    ref_id: str = "UNI-HAZ-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def notify_ufcw_steward_of_hazmat_recall(local_chapter: str, sku_id: str) -> dict:
    """Notify shop steward / local union safety rep of a hazmat product pull."""
    _req(local_chapter, "local_chapter")
    _req(sku_id, "sku_id")
    return {"op": "notify_ufcw_steward_of_hazmat_recall", "chapter": str(local_chapter), "sku_id": str(sku_id), "src": "recallstorm/comms/union_safety_notices.py"}


def specify_caustic_leaking_product_ppe(ph_level: float = 12.5) -> list[str]:
    """Return required PPE items based on chemical pH or hazard."""
    if not (0.0 <= ph_level <= 14.0):
        raise DataValidationError("ph_level must be in [0, 14]")
    if ph_level <= 2.0 or ph_level >= 11.5:
        return ["CHEMICAL_GOGGLES", "NITRILE_GAUNTLETS", "APRON"]
    return ["DISPOSABLE_GLOVES"]


def communicate_mandatory_overtime_rules(seniority_order: list[str], needed: int = 1) -> list[str]:
    """Select associates for emergency recall overtime according to CBA seniority rules."""
    if seniority_order is None or needed < 0:
        raise DataValidationError("Invalid seniority inputs")
    return list(seniority_order[:needed])


def log_associate_chemical_exposure_incident(associate_id: str, sku_id: str) -> dict:
    """Log an OSHA 300 / workers' comp incident if an associate is exposed to a leaking recalled item."""
    _req(associate_id, "associate_id")
    _req(sku_id, "sku_id")
    return {"op": "log_associate_chemical_exposure_incident", "associate_id": str(associate_id), "sku_id": str(sku_id), "src": "recallstorm/comms/union_safety_notices.py"}


def provide_ergonomic_heavy_lifting_guide(case_weight_lb: float) -> dict:
    """Require two-person team lift when recalled case weight exceeds 50 lbs."""
    if case_weight_lb <= 0:
        raise DataValidationError("case_weight_lb must be positive")
    return {"op": "provide_ergonomic_heavy_lifting_guide", "team_lift_required": case_weight_lb > 50.0, "src": "recallstorm/comms/union_safety_notices.py"}


def verify_spill_kit_availability_in_aisles(store_id: str, kits_present: int = 2) -> dict:
    """Verify hazmat spill kit availability before pulling pressurized or liquid chemical recalls."""
    _req(store_id, "store_id")
    if kits_present < 0:
        raise DataValidationError("kits_present cannot be negative")
    return {"op": "verify_spill_kit_availability_in_aisles", "store_id": str(store_id), "ready": kits_present >= 1, "src": "recallstorm/comms/union_safety_notices.py"}


def address_immunocompromised_staff_opt_out(associate_id: str, reassigned: bool = True) -> dict:
    """Reassign pregnant or immunocompromised associates away from pathogen/chemical recall pulls."""
    _req(associate_id, "associate_id")
    return {"op": "address_immunocompromised_staff_opt_out", "associate_id": str(associate_id), "reassigned": bool(reassigned), "src": "recallstorm/comms/union_safety_notices.py"}


def document_joint_safety_committee_review(committee_id: str, approved: bool = True) -> dict:
    """Document joint safety committee review of recall handling procedures."""
    _req(committee_id, "committee_id")
    return {"op": "document_joint_safety_committee_review", "committee_id": str(committee_id), "approved": bool(approved), "src": "recallstorm/comms/union_safety_notices.py"}


def distribute_sds_safety_data_sheets(sku_id: str, sds_url: str) -> dict:
    """Attach OSHA GHS Safety Data Sheet (SDS) link to handheld pull tasks."""
    _req(sku_id, "sku_id")
    _req(sds_url, "sds_url")
    return {"op": "distribute_sds_safety_data_sheets", "sku_id": str(sku_id), "sds_url": str(sds_url), "src": "recallstorm/comms/union_safety_notices.py"}


def archive_union_grievance_communications(grievance_id: str, resolved: bool = True) -> dict:
    """Archive labor relations communications related to emergency recall scheduling."""
    _req(grievance_id, "grievance_id")
    return {"op": "archive_union_grievance_communications", "grievance_id": str(grievance_id), "resolved": bool(resolved), "src": "recallstorm/comms/union_safety_notices.py"}
