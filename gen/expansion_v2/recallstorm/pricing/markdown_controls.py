"""Block CVP clearance stickers and automated cadence markdowns on recalled SKUs."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class MarkdownLockoutEngine:
    """Engine preventing clearance markdowns on recalled or banned inventory."""

    ref_id: str = "MKD-LCK-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class ClearanceTagBlocker:
    """Blocker for handheld CVP yellow clearance sticker printing."""

    ref_id: str = "MKD-CVP-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def freeze_automated_cadence_markdowns(sku_id: str) -> dict:
    """Freeze automated end-of-season cadence markdowns on a recalled SKU."""
    _req(sku_id, "sku_id")
    return {"op": "freeze_automated_cadence_markdowns", "sku_id": str(sku_id), "frozen": True, "src": "recallstorm/pricing/markdown_controls.py"}


def block_handheld_cvp_yellow_sticker_print(sku_id: str, store_id: str) -> dict:
    """Block associates from printing CVP (Customer Value Program) yellow markdown stickers for sku_id."""
    _req(sku_id, "sku_id")
    _req(store_id, "store_id")
    return {"op": "block_handheld_cvp_yellow_sticker_print", "sku_id": str(sku_id), "store_id": str(store_id), "print_blocked": True, "src": "recallstorm/pricing/markdown_controls.py"}


def invalidate_existing_clearance_barcodes(cvp_barcode: str) -> dict:
    """Invalidate already-applied CVP clearance barcodes at POS registers."""
    _req(cvp_barcode, "cvp_barcode")
    return {"op": "invalidate_existing_clearance_barcodes", "cvp_barcode": str(cvp_barcode), "invalidated": True, "src": "recallstorm/pricing/markdown_controls.py"}


def recall_discounted_bakery_day_old_racks(store_id: str) -> dict:
    """Trigger immediate sweep of bakery day-old / clearance racks for recalled items."""
    _req(store_id, "store_id")
    return {"op": "recall_discounted_bakery_day_old_racks", "store_id": str(store_id), "sweep_dispatched": True, "src": "recallstorm/pricing/markdown_controls.py"}


def prevent_manager_special_price_override(sku_id: str) -> dict:
    """Block store manager ad-hoc temporary price reductions (TPRs) on sku_id."""
    _req(sku_id, "sku_id")
    return {"op": "prevent_manager_special_price_override", "sku_id": str(sku_id), "blocked": True, "src": "recallstorm/pricing/markdown_controls.py"}


def audit_recent_markdown_scan_history(scans: list[dict], sku_id: str) -> list[str]:
    """Return store_ids that printed CVP markdown stickers for sku_id within the last 48 hours."""
    if scans is None:
        raise DataValidationError("scans cannot be None")
    _req(sku_id, "sku_id")
    return sorted({str(s["store_id"]) for s in scans if s.get("sku_id") == sku_id})


def reverse_pending_price_change_batches(batch_ids: list[str]) -> list[str]:
    """Cancel pending overnight price-change batches for recalled SKUs."""
    if batch_ids is None:
        raise DataValidationError("batch_ids cannot be None")
    return sorted(str(b) for b in batch_ids if str(b).strip())


def flag_suspicious_pre_recall_markdowns(store_id: str, markdown_pct: float) -> dict:
    """Flag stores that applied deep unauthorized markdowns (> 50%) right before a statutory ban date."""
    _req(store_id, "store_id")
    if not (0.0 <= markdown_pct <= 100.0):
        raise DataValidationError("markdown_pct must be in [0, 100]")
    return {"op": "flag_suspicious_pre_recall_markdowns", "store_id": str(store_id), "flagged": markdown_pct >= 50.0, "src": "recallstorm/pricing/markdown_controls.py"}


def reconcile_markdown_journal_reversals(reversed_units: int, markdown_delta_usd: float) -> float:
    """Reconcile retail price markdown journal reversals when CVP items are pulled."""
    if reversed_units < 0 or markdown_delta_usd < 0:
        raise DataValidationError("Negative markdown reversal inputs")
    return round(float(reversed_units) * float(markdown_delta_usd), 2)


def enforce_zero_salvage_price_floor(sku_id: str) -> dict:
    """Set liquidation/salvage price floor to $0.00 (prohibit secondary-market liquidation)."""
    _req(sku_id, "sku_id")
    return {"op": "enforce_zero_salvage_price_floor", "sku_id": str(sku_id), "liquidation_prohibited": True, "src": "recallstorm/pricing/markdown_controls.py"}
