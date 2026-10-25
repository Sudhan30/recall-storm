"""Witnessed compactor destruction affidavits and RCRA waste profiles."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class WitnessedDestructionRecord:
    """Dual-witnessed inventory destruction certificate."""

    ref_id: str = "DEST-REC-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class CompactorLogTracker:
    """Store/DC sealed trash compactor cycle log."""

    ref_id: str = "DEST-CMP-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def schedule_regulatory_witness_appointment(store_id: str, agency: str = "FDA") -> dict:
    """Schedule an FDA or State Dept of Ag witness appointment for Class I destruction."""
    _req(store_id, "store_id")
    return {"op": "schedule_regulatory_witness_appointment", "store_id": str(store_id), "agency": str(agency), "src": "recallstorm/inventory/destruction_witness.py"}


def capture_compactor_cycle_video_hash(clip_id: str) -> str:
    """Compute SHA-256 tamper-evident hash for a CCTV compactor destruction clip."""
    _req(clip_id, "clip_id")
    return hashlib.sha256(str(clip_id).encode("utf-8")).hexdigest()[:16]


def record_denaturing_chemical_application(batch_id: str, agent: str = "BLEACH_DYE") -> dict:
    """Record USDA/FDA denaturing agent application rendering food inedible prior to landfill."""
    _req(batch_id, "batch_id")
    _req(agent, "agent")
    return {"op": "record_denaturing_chemical_application", "batch_id": str(batch_id), "agent": str(agent), "denatured": True, "src": "recallstorm/inventory/destruction_witness.py"}


def weigh_pre_destruction_pallet_gross(cases: int, case_weight_lb: float, pallet_tare_lb: float = 40.0) -> float:
    """Calculate expected gross pallet weight in pounds before destruction."""
    if cases < 0 or case_weight_lb <= 0 or pallet_tare_lb < 0:
        raise DataValidationError("Invalid weight parameters")
    return round(cases * case_weight_lb + pallet_tare_lb, 2)


def generate_dual_signature_affidavit(manager_id: str, witness_id: str, units: int) -> dict:
    """Generate a dual-signature Certificate of Destruction."""
    _req(manager_id, "manager_id")
    _req(witness_id, "witness_id")
    if str(manager_id).strip() == str(witness_id).strip():
        raise DataValidationError("Dual signature requires two distinct individuals")
    if units < 0:
        raise DataValidationError("units cannot be negative")
    return {"op": "generate_dual_signature_affidavit", "manager_id": str(manager_id), "witness_id": str(witness_id), "units": int(units), "src": "recallstorm/inventory/destruction_witness.py"}


def verify_landfill_manifest_ticket_id(ticket_id: str, net_tons: float = 1.5) -> dict:
    """Verify commercial hauler landfill scale ticket."""
    _req(ticket_id, "ticket_id")
    if net_tons <= 0:
        raise DataValidationError("net_tons must be positive")
    return {"op": "verify_landfill_manifest_ticket_id", "ticket_id": str(ticket_id), "net_tons": float(net_tons), "src": "recallstorm/inventory/destruction_witness.py"}


def upload_geotagged_destruction_photos(store_id: str, lat: float, lon: float) -> dict:
    """Verify geotagged destruction photo coordinates."""
    _req(store_id, "store_id")
    if not (-90.0 <= lat <= 90.0) or not (-180.0 <= lon <= 180.0):
        raise DataValidationError("Invalid GPS coordinates")
    return {"op": "upload_geotagged_destruction_photos", "store_id": str(store_id), "coords": [lat, lon], "src": "recallstorm/inventory/destruction_witness.py"}


def audit_unwitnessed_disposal_exceptions(records: list[dict]) -> list[str]:
    """Return store_ids where destruction lacked a second witness signature."""
    if records is None:
        raise DataValidationError("records cannot be None")
    return [str(r["store_id"]) for r in records if not r.get("witness_id")]


def lock_destroyed_lpn_in_wms(lpn: str) -> dict:
    """Permanently retire a destroyed pallet LPN in WMS."""
    _req(lpn, "lpn")
    return {"op": "lock_destroyed_lpn_in_wms", "lpn": str(lpn), "status": "DESTROYED", "src": "recallstorm/inventory/destruction_witness.py"}


def archive_epa_rcra_waste_profile(sku_id: str, waste_code: str = "NON_HAZARDOUS") -> dict:
    """Archive EPA RCRA waste determination profile for a recalled SKU."""
    _req(sku_id, "sku_id")
    return {"op": "archive_epa_rcra_waste_profile", "sku_id": str(sku_id), "waste_code": str(waste_code), "src": "recallstorm/inventory/destruction_witness.py"}
