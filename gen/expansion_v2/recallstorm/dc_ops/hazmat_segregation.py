"""DOT hazard class segregation, RCRA P-list limits, and EPA waste manifests."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class HazmatQuarantineProtocol:
    """DOT/OSHA/EPA hazardous material quarantine protocol."""

    ref_id: str = "HAZ-PRT-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class RcraWasteClassifier:
    """EPA RCRA hazardous waste classifier (D-list / U-list / P-list)."""

    ref_id: str = "HAZ-RCR-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def classify_recalled_sku_by_dot_hazard_class(category: str) -> str:
    """Classify a recalled consumer product into DOT Hazard Class ('2.1_AEROSOL', '3_FLAMMABLE', '8_CORROSIVE', '9_LITHIUM', or 'NON_DOT')."""
    _req(category, "category")
    low = str(category).lower()
    if "aerosol" in low or "spray" in low or "lubricant" in low:
        return "2.1_AEROSOL"
    if "flammable" in low or "solvent" in low:
        return "3_FLAMMABLE"
    if "bleach" in low or "acid" in low or "corrosive" in low:
        return "8_CORROSIVE"
    if "battery" in low or "lithium" in low:
        return "9_LITHIUM"
    return "NON_DOT"


def segregate_flammable_aerosols_in_wire_cage(dc_id: str, cases: int) -> dict:
    """Route recalled flammable aerosols (e.g. high-VOC lubricants) to an NFPA 30B sprinklered wire cage."""
    _req(dc_id, "dc_id")
    if cases < 0:
        raise DataValidationError("cases cannot be negative")
    return {"op": "segregate_flammable_aerosols_in_wire_cage", "dc_id": str(dc_id), "cases": int(cases), "nfpa_30b_cage": True, "src": "recallstorm/dc_ops/hazmat_segregation.py"}


def check_oxidizer_vs_corrosive_incompatibility(class_a: str, class_b: str) -> dict:
    """Check chemical storage incompatibility (e.g. acids vs hypochlorites/oxidizers must be separated by >= 20 ft or firewall)."""
    _req(class_a, "class_a")
    _req(class_b, "class_b")
    pair = {str(class_a).upper(), str(class_b).upper()}
    incompatible = ("ACID" in pair and "BLEACH" in pair) or ("OXIDIZER" in pair and "FLAMMABLE" in pair)
    return {"op": "check_oxidizer_vs_corrosive_incompatibility", "incompatible": incompatible, "src": "recallstorm/dc_ops/hazmat_segregation.py"}


def assign_un_number_and_packing_group_labels(dot_class: str) -> dict:
    """Assign UN identification number and Packing Group for reverse transport."""
    _req(dot_class, "dot_class")
    un = "UN1950" if "AEROSOL" in str(dot_class).upper() else ("UN3480" if "LITHIUM" in str(dot_class).upper() else "UN1993")
    return {"op": "assign_un_number_and_packing_group_labels", "un_number": un, "packing_group": "II", "src": "recallstorm/dc_ops/hazmat_segregation.py"}


def monitor_lithium_battery_thermal_runaway_risk(temp_c: float, max_temp_c: float = 45.0) -> dict:
    """Monitor recalled lithium-ion battery quarantine drums (pack in vermiculite if temp_c > max_temp_c)."""
    if temp_c < -40.0 or max_temp_c <= 0:
        raise DataValidationError("Invalid temperature")
    return {"op": "monitor_lithium_battery_thermal_runaway_risk", "thermal_alert": temp_c > max_temp_c, "src": "recallstorm/dc_ops/hazmat_segregation.py"}


def verify_spill_containment_berm_capacity(largest_container_gal: float, total_gal: float, berm_gal: float) -> dict:
    """Verify EPA secondary containment berm holds >= max(largest_container_gal * 1.1, total_gal * 0.10)."""
    if largest_container_gal < 0 or total_gal < 0 or berm_gal < 0:
        raise DataValidationError("Negative gallon inputs")
    req_gal = max(largest_container_gal * 1.1, total_gal * 0.10)
    return {"op": "verify_spill_containment_berm_capacity", "compliant": berm_gal >= req_gal, "required_gal": round(req_gal, 2), "src": "recallstorm/dc_ops/hazmat_segregation.py"}


def generate_epa_hazardous_waste_manifest(epa_id: str, waste_codes: list[str]) -> dict:
    """Generate an EPA Form 8700-22 Uniform Hazardous Waste Manifest (e-Manifest)."""
    _req(epa_id, "epa_id")
    if not waste_codes:
        raise DataValidationError("waste_codes cannot be empty")
    return {"op": "generate_epa_hazardous_waste_manifest", "epa_id": str(epa_id), "waste_codes": sorted(waste_codes), "src": "recallstorm/dc_ops/hazmat_segregation.py"}


def coordinate_clean_harbors_lab_pack_pickup(store_id: str, drums: int = 1) -> dict:
    """Schedule licensed hazardous-waste contractor lab-pack pickup at store_id."""
    _req(store_id, "store_id")
    if drums <= 0:
        raise DataValidationError("drums must be positive")
    return {"op": "coordinate_clean_harbors_lab_pack_pickup", "store_id": str(store_id), "drums": int(drums), "src": "recallstorm/dc_ops/hazmat_segregation.py"}


def track_acute_hazardous_waste_p_list_limits(kg_accumulated: float, lqg_threshold_kg: float = 1.0) -> dict:
    """Check if accumulated P-list acute hazardous waste (e.g. nicotine > 1.0 kg/month) triggers RCRA Large Quantity Generator (LQG) status."""
    if kg_accumulated < 0 or lqg_threshold_kg <= 0:
        raise DataValidationError("Invalid kg values")
    return {"op": "track_acute_hazardous_waste_p_list_limits", "lqg_triggered": kg_accumulated >= lqg_threshold_kg, "src": "recallstorm/dc_ops/hazmat_segregation.py"}


def audit_dc_tier_ii_epcra_reporting_thresholds(lbs_on_site: float, threshold_lbs: float = 10000.0) -> dict:
    """Check EPCRA Tier II chemical inventory reporting threshold (10,000 lbs)."""
    if lbs_on_site < 0 or threshold_lbs <= 0:
        raise DataValidationError("Invalid pound values")
    return {"op": "audit_dc_tier_ii_epcra_reporting_thresholds", "reportable": lbs_on_site >= threshold_lbs, "src": "recallstorm/dc_ops/hazmat_segregation.py"}
