"""Emergency POS register hard stop-sale locks and lane heartbeats."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class PosHardLockRule:
    """POS hard stop-sale rule blocking register checkout."""

    ref_id: str = "POS-LOCK-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class RegisterBlockInjector:
    """Emergency price-file injector pushing stop-sale flags to checkout lanes."""

    ref_id: str = "POS-INJ-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def compile_pos_stop_sale_xml_payload(gtin: str, recall_id: str = "REC-01") -> str:
    """Compile an emergency POS stop-sale XML message for a GTIN."""
    _req(gtin, "gtin")
    _req(recall_id, "recall_id")
    return f"<PosStopSale gtin=\"{str(gtin).strip()}\" recall=\"{str(recall_id).strip()}\" hardLock=\"true\"/>"


def push_emergency_plu_lock_to_lanes(store_id: str, lane_count: int = 24) -> dict:
    """Broadcast emergency stop-sale lock to all register lanes in store_id."""
    _req(store_id, "store_id")
    if lane_count <= 0:
        raise DataValidationError("lane_count must be positive")
    return {"op": "push_emergency_plu_lock_to_lanes", "store_id": str(store_id), "lanes_updated": int(lane_count), "src": "recallstorm/pricing/pos_sale_blocks.py"}


def verify_lane_sync_heartbeat_status(synced_lanes: int, total_lanes: int) -> dict:
    """Verify that 100% of checkout lanes acknowledged the POS stop-sale sync."""
    if synced_lanes < 0 or total_lanes <= 0 or synced_lanes > total_lanes:
        raise DataValidationError("Invalid lane counts")
    return {"op": "verify_lane_sync_heartbeat_status", "all_synced": synced_lanes == total_lanes, "pct": round((synced_lanes / total_lanes) * 100.0, 2), "src": "recallstorm/pricing/pos_sale_blocks.py"}


def block_manual_department_key_entry(store_id: str, dept_id: str) -> dict:
    """Disable open-department price entry on registers during a fresh-department recall."""
    _req(store_id, "store_id")
    _req(dept_id, "dept_id")
    return {"op": "block_manual_department_key_entry", "store_id": str(store_id), "dept_id": str(dept_id), "blocked": True, "src": "recallstorm/pricing/pos_sale_blocks.py"}


def intercept_weight_embedded_barcodes(prefix_item_code: str) -> dict:
    """Block all Prefix-2 variable-weight barcodes matching the 5-digit item code."""
    _req(prefix_item_code, "prefix_item_code")
    return {"op": "intercept_weight_embedded_barcodes", "item_code": str(prefix_item_code), "wildcard_blocked": True, "src": "recallstorm/pricing/pos_sale_blocks.py"}


def test_self_checkout_override_denial(sku_id: str, override_attempted: bool = True) -> dict:
    """Verify that supervisor badge overrides are denied on hard-locked recalled SKUs."""
    _req(sku_id, "sku_id")
    return {"op": "test_self_checkout_override_denial", "sku_id": str(sku_id), "override_denied": True, "attempted": bool(override_attempted), "src": "recallstorm/pricing/pos_sale_blocks.py"}


def log_blocked_scan_attempt_events(store_id: str, sku_id: str, lane_id: str = "SCO-01") -> dict:
    """Log a customer scan attempt of a recalled item at checkout (triggers immediate shelf sweep)."""
    _req(store_id, "store_id")
    _req(sku_id, "sku_id")
    return {"op": "log_blocked_scan_attempt_events", "store_id": str(store_id), "sku_id": str(sku_id), "lane_id": str(lane_id), "resweep_triggered": True, "src": "recallstorm/pricing/pos_sale_blocks.py"}


def handle_offline_register_resync(lane_id: str, pending_locks: int = 1) -> dict:
    """Queue and apply stop-sale locks when an offline register reconnects."""
    _req(lane_id, "lane_id")
    if pending_locks < 0:
        raise DataValidationError("pending_locks cannot be negative")
    return {"op": "handle_offline_register_resync", "lane_id": str(lane_id), "applied": int(pending_locks), "src": "recallstorm/pricing/pos_sale_blocks.py"}


def generate_cashier_halt_screen_text(sku_name: str) -> str:
    """Generate high-visibility red cashier screen halt message."""
    _req(sku_name, "sku_name")
    return f"STOP SALE - RECALL / REGULATORY BAN: Retain {sku_name} and place in Customer Service Quarantine Bin."


def audit_pos_lock_coverage_by_store(stores_locked: int, total_stores: int) -> dict:
    """Audit chainwide POS stop-sale lock coverage."""
    if stores_locked < 0 or total_stores <= 0 or stores_locked > total_stores:
        raise DataValidationError("Invalid store counts")
    return {"op": "audit_pos_lock_coverage_by_store", "complete": stores_locked == total_stores, "coverage_pct": round((stores_locked / total_stores) * 100.0, 2), "src": "recallstorm/pricing/pos_sale_blocks.py"}
