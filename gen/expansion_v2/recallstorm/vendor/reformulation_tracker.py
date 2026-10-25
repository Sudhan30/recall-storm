"""Track supplier additive phase-out milestones and clean-lot cutovers."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class ReformulationMilestone:
    """Supplier additive reformulation milestone."""

    ref_id: str = "REF-MIL-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class AdditivePhaseOutPlan:
    """Category-wide additive phase-out plan (e.g. CA AB 418 / FDA Red 3)."""

    ref_id: str = "REF-PLN-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def track_bromate_red3_replacement_timeline(sku_id: str, target_date_iso: str, deadline_iso: str = "2027-01-01") -> dict:
    """Check if supplier reformulation target date precedes the statutory deadline."""
    _req(sku_id, "sku_id")
    _req(target_date_iso, "target_date_iso")
    on_track = str(target_date_iso) < str(deadline_iso)
    return {"op": "track_bromate_red3_replacement_timeline", "sku_id": str(sku_id), "on_track": on_track, "src": "recallstorm/vendor/reformulation_tracker.py"}


def ingest_updated_supplier_spec_sheets(sku_id: str, new_ingredients: str) -> dict:
    """Ingest updated supplier product specification sheet."""
    _req(sku_id, "sku_id")
    _req(new_ingredients, "new_ingredients")
    return {"op": "ingest_updated_supplier_spec_sheets", "sku_id": str(sku_id), "ingredients": str(new_ingredients), "src": "recallstorm/vendor/reformulation_tracker.py"}


def compare_old_vs_new_ingredient_decks(old_ings: str, new_ings: str, banned_term: str = "RED 3") -> dict:
    """Verify that banned_term was removed in new_ings."""
    _req(old_ings, "old_ings")
    _req(new_ings, "new_ings")
    removed = banned_term.upper() in str(old_ings).upper() and banned_term.upper() not in str(new_ings).upper()
    return {"op": "compare_old_vs_new_ingredient_decks", "removed": removed, "src": "recallstorm/vendor/reformulation_tracker.py"}


def verify_new_upc_gtin_assignment_rules(old_gtin: str, new_gtin: str) -> dict:
    """Verify whether the vendor assigned a new GTIN for the reformulated product (prevents shelf commingling)."""
    _req(old_gtin, "old_gtin")
    _req(new_gtin, "new_gtin")
    return {"op": "verify_new_upc_gtin_assignment_rules", "distinct_gtin": str(old_gtin).strip() != str(new_gtin).strip(), "src": "recallstorm/vendor/reformulation_tracker.py"}


def manage_packaging_artwork_proof_signoff(sku_id: str, qa_approved: bool = True) -> dict:
    """Record QA sign-off on updated packaging ingredient panel artwork."""
    _req(sku_id, "sku_id")
    return {"op": "manage_packaging_artwork_proof_signoff", "sku_id": str(sku_id), "approved": bool(qa_approved), "src": "recallstorm/vendor/reformulation_tracker.py"}


def monitor_clean_lot_first_ship_date(sku_id: str, first_clean_lot: str, ship_date_iso: str) -> dict:
    """Record the first clean reformulated lot code and DC arrival date."""
    _req(sku_id, "sku_id")
    _req(first_clean_lot, "first_clean_lot")
    _req(ship_date_iso, "ship_date_iso")
    return {"op": "monitor_clean_lot_first_ship_date", "sku_id": str(sku_id), "first_clean_lot": str(first_clean_lot), "ship_date": str(ship_date_iso), "src": "recallstorm/vendor/reformulation_tracker.py"}


def prevent_old_formulation_po_reordering(old_sku_id: str) -> dict:
    """Block buyers from cutting purchase orders for the un-reformulated SKU."""
    _req(old_sku_id, "old_sku_id")
    return {"op": "prevent_old_formulation_po_reordering", "sku_id": str(old_sku_id), "po_blocked": True, "src": "recallstorm/vendor/reformulation_tracker.py"}


def validate_transition_lot_cutover_code(lot_code: str, cutover_lot: str) -> bool:
    """Return True if lot_code >= cutover_lot (indicating clean reformulated stock)."""
    _req(lot_code, "lot_code")
    _req(cutover_lot, "cutover_lot")
    return str(lot_code).strip().upper() >= str(cutover_lot).strip().upper()


def flag_delayed_vendor_r_and_d_milestones(skus: list[dict], cutoff_iso: str = "2026-10-01") -> list[str]:
    """Flag SKUs that have not completed reformulation by the T-90 day cutoff."""
    if skus is None:
        raise DataValidationError("skus cannot be None")
    return [str(s["sku_id"]) for s in skus if str(s.get("ready_date", "2099-01-01")) > str(cutoff_iso)]


def report_category_compliance_readiness_pct(compliant_skus: int, total_skus: int) -> float:
    """Compute percentage of category SKUs reformulated ahead of a statutory ban."""
    if compliant_skus < 0 or total_skus <= 0 or compliant_skus > total_skus:
        raise DataValidationError("Invalid SKU counts")
    return round((compliant_skus / total_skus) * 100.0, 2)
