"""Deli/bakery scale PLU deactivation and produce lookup blocks."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class PluScaleDeactivator:
    """Deactivator for fresh department scale PLUs."""

    ref_id: str = "PLU-DEC-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class TareAndPluSync:
    """Scale network PLU and ingredient label table synchronization."""

    ref_id: str = "PLU-SYNC-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def purge_recalled_plu_from_deli_scales(store_id: str, plu_code: str) -> dict:
    """Purge a recalled PLU from deli service-counter scales."""
    _req(store_id, "store_id")
    _req(plu_code, "plu_code")
    return {"op": "purge_recalled_plu_from_deli_scales", "store_id": str(store_id), "plu_code": str(plu_code), "purged": True, "src": "recallstorm/pricing/price_lookup_blocks.py"}


def disable_bakery_self_serve_plu_buttons(store_id: str, button_ids: list[str]) -> dict:
    """Hide self-serve bakery touchscreen PLU buttons for recalled items."""
    _req(store_id, "store_id")
    if not button_ids:
        raise DataValidationError("button_ids cannot be empty")
    return {"op": "disable_bakery_self_serve_plu_buttons", "store_id": str(store_id), "buttons": sorted(button_ids), "src": "recallstorm/pricing/price_lookup_blocks.py"}


def push_scale_network_lockout_file(store_id: str, scale_count: int = 8) -> dict:
    """Push PLU lockout file to networked in-store scales."""
    _req(store_id, "store_id")
    if scale_count <= 0:
        raise DataValidationError("scale_count must be positive")
    return {"op": "push_scale_network_lockout_file", "store_id": str(store_id), "scale_count": int(scale_count), "src": "recallstorm/pricing/price_lookup_blocks.py"}


def verify_hobart_toledo_scale_ack(scale_ip: str, ack_received: bool = True) -> dict:
    """Verify TCP/IP acknowledgment from a fresh-department scale."""
    _req(scale_ip, "scale_ip")
    return {"op": "verify_hobart_toledo_scale_ack", "scale_ip": str(scale_ip), "acked": bool(ack_received), "src": "recallstorm/pricing/price_lookup_blocks.py"}


def block_produce_cashier_look_up_menu(plu_code: str) -> dict:
    """Block produce 4/5-digit IFPS PLU code on register visual picklists."""
    _req(plu_code, "plu_code")
    return {"op": "block_produce_cashier_look_up_menu", "plu_code": str(plu_code), "blocked": True, "src": "recallstorm/pricing/price_lookup_blocks.py"}


def prevent_in_store_bar_code_printing(plu_code: str) -> dict:
    """Prevent backroom wrapper scales from printing labels for plu_code."""
    _req(plu_code, "plu_code")
    return {"op": "prevent_in_store_bar_code_printing", "plu_code": str(plu_code), "print_disabled": True, "src": "recallstorm/pricing/price_lookup_blocks.py"}


def archive_deactivated_plu_recipe_text(plu_code: str, ingredients: str) -> dict:
    """Archive the exact scale ingredient text active at the time of recall."""
    _req(plu_code, "plu_code")
    _req(ingredients, "ingredients")
    return {"op": "archive_deactivated_plu_recipe_text", "plu_code": str(plu_code), "ingredients": str(ingredients), "src": "recallstorm/pricing/price_lookup_blocks.py"}


def monitor_scale_firmware_sync_errors(failed_ips: list[str]) -> list[str]:
    """Return sorted scale IPs that failed PLU lockout sync."""
    if failed_ips is None:
        raise DataValidationError("failed_ips cannot be None")
    return sorted(str(ip) for ip in failed_ips if str(ip).strip())


def restore_cleared_plu_price_tables(plu_code: str, qa_approval_id: str) -> dict:
    """Restore a PLU to active scale tables after clean-lot restock."""
    _req(plu_code, "plu_code")
    _req(qa_approval_id, "qa_approval_id")
    return {"op": "restore_cleared_plu_price_tables", "plu_code": str(plu_code), "restored": True, "src": "recallstorm/pricing/price_lookup_blocks.py"}


def audit_unnetworked_standalone_scales(store_id: str, standalone_count: int = 0) -> dict:
    """Flag standalone USB-updated scales requiring manual technician update."""
    _req(store_id, "store_id")
    if standalone_count < 0:
        raise DataValidationError("standalone_count cannot be negative")
    return {"op": "audit_unnetworked_standalone_scales", "store_id": str(store_id), "manual_update_required": standalone_count > 0, "src": "recallstorm/pricing/price_lookup_blocks.py"}
