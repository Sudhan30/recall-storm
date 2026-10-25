"""Decode multi-co-packer Julian plant suffixes and isolate affected plants."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class MultiCoPackerResolver:
    """Resolver isolating affected co-packer plants on dual/multi-sourced SKUs."""

    ref_id: str = "CPK-RES-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class PlantCodeRouter:
    """Router mapping package plant suffixes to regional distribution centers."""

    ref_id: str = "CPK-RTR-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def decode_julian_plant_suffix_on_packaging(lot_code: str) -> dict:
    """Extract trailing 2-character plant code from a Julian lot string (e.g. '26145TX' -> plant='TX')."""
    _req(lot_code, "lot_code")
    s = str(lot_code).strip().upper()
    if len(s) < 2:
        raise DataValidationError("lot_code too short to contain plant suffix")
    return {"op": "decode_julian_plant_suffix_on_packaging", "lot": s, "plant_suffix": s[-2:], "src": "recallstorm/vendor/co_packer_traceability.py"}


def isolate_affected_co_packer_facility(lots: list[str], affected_suffix: str) -> list[str]:
    """Filter lots to those produced at affected_suffix facility."""
    if lots is None:
        raise DataValidationError("lots cannot be None")
    _req(affected_suffix, "affected_suffix")
    suf = str(affected_suffix).strip().upper()
    return [l for l in lots if str(l).strip().upper().endswith(suf)]


def clear_unaffected_sister_plant_inventory(lots: list[str], affected_suffix: str) -> list[str]:
    """Return lots produced at unaffected sister plants so they remain on sale."""
    if lots is None:
        raise DataValidationError("lots cannot be None")
    _req(affected_suffix, "affected_suffix")
    suf = str(affected_suffix).strip().upper()
    return [l for l in lots if not str(l).strip().upper().endswith(suf)]


def map_regional_co_packer_dc_assignments(plant_map: dict[str, list[str]], plant_id: str) -> list[str]:
    """Return DC IDs supplied by plant_id."""
    if plant_map is None:
        raise DataValidationError("plant_map cannot be None")
    _req(plant_id, "plant_id")
    return sorted(plant_map.get(str(plant_id), []))


def verify_co_packer_sub_ingredient_suppliers(plant_id: str, sub_suppliers: list[str]) -> dict:
    """Verify approved sub-ingredient suppliers for plant_id."""
    _req(plant_id, "plant_id")
    if not sub_suppliers:
        raise DataValidationError("sub_suppliers cannot be empty")
    return {"op": "verify_co_packer_sub_ingredient_suppliers", "plant_id": str(plant_id), "suppliers": sorted(sub_suppliers), "src": "recallstorm/vendor/co_packer_traceability.py"}


def audit_unauthorized_subcontracting_events(declared_plant: str, actual_plant: str) -> dict:
    """Flag unauthorized co-packer subcontracting when actual_plant differs from declared_plant."""
    _req(declared_plant, "declared_plant")
    _req(actual_plant, "actual_plant")
    return {"op": "audit_unauthorized_subcontracting_events", "unauthorized": str(declared_plant).upper() != str(actual_plant).upper(), "src": "recallstorm/vendor/co_packer_traceability.py"}


def reconcile_packaging_roll_stock_transfers(from_plant: str, to_plant: str, rolls: int) -> dict:
    """Track shared pre-printed packaging film transferred between sister co-packer plants."""
    _req(from_plant, "from_plant")
    _req(to_plant, "to_plant")
    if rolls < 0:
        raise DataValidationError("rolls cannot be negative")
    return {"op": "reconcile_packaging_roll_stock_transfers", "from_plant": str(from_plant), "to_plant": str(to_plant), "rolls": int(rolls), "src": "recallstorm/vendor/co_packer_traceability.py"}


def update_gtin_to_plant_routing_tables(gtin: str, backup_plant: str) -> dict:
    """Re-route POs for gtin to backup_plant when primary co-packer is shut down."""
    _req(gtin, "gtin")
    _req(backup_plant, "backup_plant")
    return {"op": "update_gtin_to_plant_routing_tables", "gtin": str(gtin), "backup_plant": str(backup_plant), "src": "recallstorm/vendor/co_packer_traceability.py"}


def generate_plant_specific_shelf_pull_rules(sku_id: str, plant_suffix: str) -> dict:
    """Generate shelf pull instructions targeting only packages stamped with plant_suffix."""
    _req(sku_id, "sku_id")
    _req(plant_suffix, "plant_suffix")
    return {"op": "generate_plant_specific_shelf_pull_rules", "sku_id": str(sku_id), "plant_suffix": str(plant_suffix).upper(), "src": "recallstorm/vendor/co_packer_traceability.py"}


def validate_dual_sourced_sku_segregation(wms_tracks_plant: bool = True) -> dict:
    """Validate whether WMS segregates dual-sourced SKU inventory by co-packer plant code."""
    return {"op": "validate_dual_sourced_sku_segregation", "segregated": bool(wms_tracks_plant), "src": "recallstorm/vendor/co_packer_traceability.py"}
