"""Intercept flow-through cross-dock pallets before store loading."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class CrossDockHoldInterceptor:
    """Interceptor for DC flow-through / cross-dock store pallets."""

    ref_id: str = "XDOCK-INT-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class FlowThroughSplitter:
    """Splitter for multi-store master cartons on cross-dock lanes."""

    ref_id: str = "XDOCK-SPL-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def identify_pre_allocated_cross_dock_pallets(pallets: list[dict], sku_id: str) -> list[str]:
    """Return LPNs of cross-dock pallets carrying sku_id."""
    if pallets is None:
        raise DataValidationError("pallets cannot be None")
    _req(sku_id, "sku_id")
    return [str(p["lpn"]) for p in pallets if sku_id in p.get("skus", [])]


def break_store_assigned_pallet_ties(lpn: str, store_id: str) -> dict:
    """Unbind a pre-allocated cross-dock pallet from its outbound store assignment."""
    _req(lpn, "lpn")
    _req(store_id, "store_id")
    return {"op": "break_store_assigned_pallet_ties", "lpn": str(lpn), "unbound_store": str(store_id), "src": "recallstorm/inventory/cross_dock_allocation.py"}


def divert_flow_through_to_dc_hold(lpn: str, hold_zone: str = "DC-QZONE-01") -> dict:
    """Divert a flow-through pallet on the mechanized sorter to hold_zone."""
    _req(lpn, "lpn")
    return {"op": "divert_flow_through_to_dc_hold", "lpn": str(lpn), "hold_zone": str(hold_zone), "src": "recallstorm/inventory/cross_dock_allocation.py"}


def recalculation_store_allocation_shorts(planned_cases: int, cut_cases: int) -> int:
    """Recalculate outbound store delivery cases after cutting recalled cross-dock cases."""
    if planned_cases < 0 or cut_cases < 0 or cut_cases > planned_cases:
        raise DataValidationError("Invalid planned or cut cases")
    return int(planned_cases) - int(cut_cases)


def update_wms_put_to_store_lights(aisle: str, sku_id: str) -> dict:
    """Extinguish Put-To-Light (PTL) store sortation lights for a recalled SKU."""
    _req(aisle, "aisle")
    _req(sku_id, "sku_id")
    return {"op": "update_wms_put_to_store_lights", "aisle": str(aisle), "sku_id": str(sku_id), "lights_off": True, "src": "recallstorm/inventory/cross_dock_allocation.py"}


def cancel_outbound_shipping_labels(label_ids: list[str]) -> list[str]:
    """Void outbound UCC-128 / GS1-128 store shipping labels for intercepted cases."""
    if label_ids is None:
        raise DataValidationError("label_ids cannot be None")
    return sorted(str(l) for l in label_ids if str(l).strip())


def record_cross_dock_interception_scan(dc_id: str, lpn: str) -> dict:
    """Record RF interception scan at DC cross-dock lane."""
    _req(dc_id, "dc_id")
    _req(lpn, "lpn")
    return {"op": "record_cross_dock_interception_scan", "dc_id": str(dc_id), "lpn": str(lpn), "src": "recallstorm/inventory/cross_dock_allocation.py"}


def balance_multi_store_master_cartons(total_subpacks: int, stores_count: int) -> int:
    """Compute subpacks per store when breaking a master carton."""
    if total_subpacks < 0 or stores_count <= 0:
        raise DataValidationError("Invalid subpacks or stores_count")
    return total_subpacks // stores_count


def notify_merchandising_of_cut_allocations(sku_id: str, cut_cases: int) -> dict:
    """Notify merchandising replenishment desk of cross-dock allocation cuts."""
    _req(sku_id, "sku_id")
    if cut_cases < 0:
        raise DataValidationError("cut_cases cannot be negative")
    return {"op": "notify_merchandising_of_cut_allocations", "sku_id": str(sku_id), "cut_cases": int(cut_cases), "src": "recallstorm/inventory/cross_dock_allocation.py"}


def release_uncontaminated_sibling_cases(lpn: str, clean_cases: int) -> dict:
    """Release unaffected sibling SKUs stripped from a mixed cross-dock pallet."""
    _req(lpn, "lpn")
    if clean_cases < 0:
        raise DataValidationError("clean_cases cannot be negative")
    return {"op": "release_uncontaminated_sibling_cases", "lpn": str(lpn), "clean_cases": int(clean_cases), "src": "recallstorm/inventory/cross_dock_allocation.py"}
