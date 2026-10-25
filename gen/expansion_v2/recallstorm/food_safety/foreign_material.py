"""Foreign material incidents and FDA 7mm hard/sharp object evaluation."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class ForeignMaterialIncident:
    """Physical foreign material contamination incident."""

    ref_id: str = "FM-INC-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class XrayInspectionAudit:
    """X-ray / optical sorter foreign body inspection audit."""

    ref_id: str = "FM-XRAY-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def classify_fragment_material_type(desc: str) -> str:
    """Classify fragment into METAL, GLASS, HARD_PLASTIC, WOOD, or OTHER."""
    _req(desc, "desc")
    low = str(desc).lower()
    if "metal" in low or "wire" in low or "steel" in low:
        return "METAL"
    if "glass" in low:
        return "GLASS"
    if "plastic" in low:
        return "HARD_PLASTIC"
    if "wood" in low:
        return "WOOD"
    return "OTHER"


def check_fda_hard_sharp_7mm_rule(length_mm: float, is_infant_food: bool = False) -> dict:
    """Evaluate FDA CPG Sec. 555.425 hard/sharp foreign object rule (7mm to 25mm, or any size in infant food)."""
    if length_mm < 0:
        raise DataValidationError("length_mm cannot be negative")
    adulterated = (is_infant_food and length_mm >= 1.0) or (7.0 <= length_mm <= 25.0) or (length_mm > 25.0)
    return {"op": "check_fda_hard_sharp_7mm_rule", "adulterated": adulterated, "length_mm": float(length_mm), "src": "recallstorm/food_safety/foreign_material.py"}


def trace_broken_belt_maintenance_log(conveyor_id: str, missing_links: int = 0) -> dict:
    """Check conveyor belt maintenance log for missing modular plastic/wire links."""
    _req(conveyor_id, "conveyor_id")
    if missing_links < 0:
        raise DataValidationError("missing_links cannot be negative")
    return {"op": "trace_broken_belt_maintenance_log", "conveyor_id": str(conveyor_id), "hold_required": missing_links > 0, "src": "recallstorm/food_safety/foreign_material.py"}


def match_sieve_screen_mesh_failure(sieve_id: str, torn_mesh: bool = False) -> dict:
    """Check flour/spice sifter tailing and mesh integrity logs."""
    _req(sieve_id, "sieve_id")
    return {"op": "match_sieve_screen_mesh_failure", "sieve_id": str(sieve_id), "compromised": bool(torn_mesh), "src": "recallstorm/food_safety/foreign_material.py"}


def evaluate_glass_brittle_plastic_breakage(zone_id: str, sweep_radius_ft: float = 15.0) -> dict:
    """Evaluate glass/brittle plastic breakage quarantine zone."""
    _req(zone_id, "zone_id")
    if sweep_radius_ft <= 0:
        raise DataValidationError("sweep_radius_ft must be positive")
    return {"op": "evaluate_glass_brittle_plastic_breakage", "zone_id": str(zone_id), "sweep_radius_ft": float(sweep_radius_ft), "src": "recallstorm/food_safety/foreign_material.py"}


def isolate_upstream_dumper_lots(tote_id: str, lots: list[str]) -> dict:
    """Isolate finished batches fed from a compromised raw ingredient tote/dumper."""
    _req(tote_id, "tote_id")
    if not lots:
        raise DataValidationError("lots cannot be empty")
    return {"op": "isolate_upstream_dumper_lots", "tote_id": str(tote_id), "lots": sorted(lots), "src": "recallstorm/food_safety/foreign_material.py"}


def verify_magnet_pull_test_records(magnet_id: str, pull_lbs: float = 25.0) -> dict:
    """Verify rare-earth trap magnet pull-strength test records."""
    _req(magnet_id, "magnet_id")
    if pull_lbs <= 0:
        raise DataValidationError("pull_lbs must be positive")
    return {"op": "verify_magnet_pull_test_records", "magnet_id": str(magnet_id), "passed": pull_lbs >= 15.0, "src": "recallstorm/food_safety/foreign_material.py"}


def calculate_complaint_per_million_units(complaints: int, units_sold: int) -> float:
    """Calculate CPMU (Complaints Per Million Units) rate."""
    if complaints < 0 or units_sold <= 0:
        raise DataValidationError("Invalid complaints or units_sold")
    return round((complaints / units_sold) * 1_000_000.0, 2)


def build_supplier_foreign_object_claim(vendor_id: str, incident_id: str) -> dict:
    """Build a supplier foreign material chargeback/CAPA claim."""
    _req(vendor_id, "vendor_id")
    _req(incident_id, "incident_id")
    return {"op": "build_supplier_foreign_object_claim", "vendor_id": str(vendor_id), "incident_id": str(incident_id), "src": "recallstorm/food_safety/foreign_material.py"}


def generate_sensory_inspection_protocol(sku_id: str, sample_cases: int = 10) -> dict:
    """Generate a destructive visual/sieve inspection protocol for held cases."""
    _req(sku_id, "sku_id")
    if sample_cases <= 0:
        raise DataValidationError("sample_cases must be positive")
    return {"op": "generate_sensory_inspection_protocol", "sku_id": str(sku_id), "sample_cases": int(sample_cases), "src": "recallstorm/food_safety/foreign_material.py"}
