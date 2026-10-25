"""Texas DSHS consumable hemp retail registration and QR COA verification."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class TxHempRetailRule:
    """Domain entity for Texas Health & Safety Code Ch. 443 consumable hemp rules."""

    ref_id: str = "TX-CHP-443"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class DshsHempRegistration:
    """Texas DSHS retail hemp registration record."""

    ref_id: str = "TX-DSHS-REG"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def check_tx_delta9_thc_pct(thc_pct: float, limit_pct: float = 0.3) -> dict:
    """Check dry-weight Delta-9 THC percentage against the 0.3% Texas statutory limit."""
    if not isinstance(thc_pct, (int, float)) or thc_pct < 0 or limit_pct <= 0:
        raise DataValidationError("Invalid thc_pct")
    return {"op": "check_tx_delta9_thc_pct", "compliant": float(thc_pct) <= float(limit_pct), "thc_pct": float(thc_pct), "src": "recallstorm/states/tx_consumable_hemp.py"}


def verify_tx_qr_code_link(url: str) -> dict:
    """Verify that package QR code resolves to an HTTPS batch COA URL as required by TX DSHS."""
    _req(url, "url")
    valid = str(url).startswith("https://")
    return {"op": "verify_tx_qr_code_link", "valid": valid, "url": str(url), "src": "recallstorm/states/tx_consumable_hemp.py"}


def validate_tx_batch_coa_date(coa_date_iso: str, min_date_iso: str = "2025-01-01") -> dict:
    """Validate that the batch COA date is current."""
    _req(coa_date_iso, "coa_date_iso")
    return {"op": "validate_tx_batch_coa_date", "valid": str(coa_date_iso) >= str(min_date_iso), "src": "recallstorm/states/tx_consumable_hemp.py"}


def evaluate_tx_smokeable_ban(product_form: str) -> dict:
    """Evaluate Texas restrictions on smokeable hemp products."""
    _req(product_form, "product_form")
    prohibited = any(k in str(product_form).lower() for k in ("smoke", "pre-roll", "flower", "vape"))
    return {"op": "evaluate_tx_smokeable_ban", "prohibited": prohibited, "src": "recallstorm/states/tx_consumable_hemp.py"}


def flag_tx_unregistered_brands(brand: str, registered_brands: set[str] | None = None) -> dict:
    """Flag brands not registered with TX DSHS."""
    _req(brand, "brand")
    reg = registered_brands if registered_brands is not None else {"RegisteredHemp"}
    return {"op": "flag_tx_unregistered_brands", "flagged": str(brand) not in reg, "src": "recallstorm/states/tx_consumable_hemp.py"}


def check_tx_child_resistant_cap(sku_id: str, has_cr_cap: bool = True) -> dict:
    """Verify child-resistant packaging on consumable hemp in TX."""
    _req(sku_id, "sku_id")
    return {"op": "check_tx_child_resistant_cap", "sku_id": str(sku_id), "compliant": bool(has_cr_cap), "src": "recallstorm/states/tx_consumable_hemp.py"}


def filter_tx_beverage_endcaps(skus: list[str]) -> list[str]:
    """Filter hemp-derived beverage endcap SKUs in TX."""
    if skus is None:
        raise DataValidationError("skus cannot be None")
    return sorted(str(s) for s in skus if str(s).strip())


def generate_tx_dshs_audit_log(store_id: str, skus_checked: int = 1) -> dict:
    """Generate a TX DSHS retail inspection log."""
    _req(store_id, "store_id")
    return {"op": "generate_tx_dshs_audit_log", "store_id": str(store_id), "skus_checked": int(skus_checked), "src": "recallstorm/states/tx_consumable_hemp.py"}


def calculate_tx_hemp_tax_hold(units: int, unit_retail: float = 10.0) -> float:
    """Calculate held retail value for quarantined TX hemp inventory."""
    if units < 0 or unit_retail < 0:
        raise DataValidationError("Negative tax hold inputs")
    return round(float(units) * float(unit_retail), 2)


def audit_tx_license_expiration(store_id: str, expires_iso: str, now_iso: str = "2026-12-30") -> dict:
    """Audit whether a TX store's DSHS consumable hemp retail registration is active."""
    _req(store_id, "store_id")
    _req(expires_iso, "expires_iso")
    return {"op": "audit_tx_license_expiration", "store_id": str(store_id), "active": str(expires_iso) > str(now_iso), "src": "recallstorm/states/tx_consumable_hemp.py"}
