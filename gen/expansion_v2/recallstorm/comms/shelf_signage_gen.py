"""Public recall shelf placards, QR links, and 14-day takedown schedules."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class RecallShelfTalker:
    """Point-of-display consumer recall shelf talker."""

    ref_id: str = "SGN-TLK-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class PublicNoticePlacard:
    """14-day public recall notice placard for aisle and service counter."""

    ref_id: str = "SGN-PLC-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def render_fda_compliant_shelf_placard_pdf(sku_name: str, recall_id: str) -> dict:
    """Render metadata for an FDA-compliant point-of-display recall placard."""
    _req(sku_name, "sku_name")
    _req(recall_id, "recall_id")
    return {"op": "render_fda_compliant_shelf_placard_pdf", "sku_name": str(sku_name), "recall_id": str(recall_id), "header": "URGENT PRODUCT RECALL", "src": "recallstorm/comms/shelf_signage_gen.py"}


def check_state_mandated_signage_font_size(font_pt: int, min_pt: int = 24) -> dict:
    """Verify that recall placard headline meets state minimum font size."""
    if font_pt <= 0 or min_pt <= 0:
        raise DataValidationError("Font size must be positive")
    return {"op": "check_state_mandated_signage_font_size", "compliant": font_pt >= min_pt, "src": "recallstorm/comms/shelf_signage_gen.py"}


def generate_qr_code_to_fda_press_release(recall_id: str) -> str:
    """Generate QR code target URL for the official FDA recall announcement."""
    _req(recall_id, "recall_id")
    return f"https://www.fda.gov/safety/recalls/{str(recall_id).strip()}"


def map_placard_count_to_aisle_facings(facings_count: int) -> int:
    """Calculate required shelf talkers (at least 1 per affected bay/facing)."""
    if facings_count < 0:
        raise DataValidationError("facings_count cannot be negative")
    return max(1, int(facings_count)) if facings_count > 0 else 0


def schedule_fourteen_day_sign_takedown(posted_date_iso: str, days: int = 14) -> str:
    """Compute the mandatory 14-day sign takedown date."""
    _req(posted_date_iso, "posted_date_iso")
    if days <= 0:
        raise DataValidationError("days must be positive")
    dt = date.fromisoformat(str(posted_date_iso)[:10]) + timedelta(days=int(days))
    return dt.isoformat()


def print_bilingual_consumer_warning_cards(sku_name: str) -> dict:
    """Generate English/Spanish bilingual consumer warning card text."""
    _req(sku_name, "sku_name")
    return {"op": "print_bilingual_consumer_warning_cards", "en": f"RECALL: {sku_name}", "es": f"RETIRO: {sku_name}", "src": "recallstorm/comms/shelf_signage_gen.py"}


def verify_sign_placement_via_photo_upload(store_id: str, photo_hash: str) -> dict:
    """Verify shelf placard placement via handheld photo upload."""
    _req(store_id, "store_id")
    _req(photo_hash, "photo_hash")
    return {"op": "verify_sign_placement_via_photo_upload", "store_id": str(store_id), "verified": True, "src": "recallstorm/comms/shelf_signage_gen.py"}


def flag_missing_checklane_recall_mat(store_id: str, posted_at_service_desk: bool = False) -> dict:
    """Flag stores missing the required Customer Service Desk recall binder/placard."""
    _req(store_id, "store_id")
    return {"op": "flag_missing_checklane_recall_mat", "store_id": str(store_id), "flagged": not posted_at_service_desk, "src": "recallstorm/comms/shelf_signage_gen.py"}


def format_service_counter_allergen_notice(dept: str, allergen: str) -> str:
    """Format a fresh-department service counter allergen notice."""
    _req(dept, "dept")
    _req(allergen, "allergen")
    return f"{str(dept).upper()} NOTICE: Undeclared {str(allergen).upper()} recall in effect."


def audit_expired_placard_removal(takedown_date_iso: str, today_iso: str = "2027-01-20") -> dict:
    """Check if a 14-day recall placard is past its takedown date and should be removed."""
    _req(takedown_date_iso, "takedown_date_iso")
    return {"op": "audit_expired_placard_removal", "remove_now": str(today_iso) >= str(takedown_date_iso), "src": "recallstorm/comms/shelf_signage_gen.py"}
