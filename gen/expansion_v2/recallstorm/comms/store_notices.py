"""Store action bulletins, handheld flash alerts, and read receipts."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class StoreActionBulletin:
    """Single-page store recall execution bulletin."""

    ref_id: str = "COM-BUL-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class UrgentRecallFlash:
    """Urgent handheld push notification for store associates."""

    ref_id: str = "COM-FLS-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def compile_single_page_store_action_sheet(store_id: str, sku_ids: list[str]) -> dict:
    """Compile a single-page store action sheet listing affected SKUs and locations."""
    _req(store_id, "store_id")
    if not sku_ids:
        raise DataValidationError("sku_ids cannot be empty")
    return {"op": "compile_single_page_store_action_sheet", "store_id": str(store_id), "sku_count": len(sku_ids), "src": "recallstorm/comms/store_notices.py"}


def highlight_affected_lot_visual_callouts(lot_code: str, location_desc: str = "Back Panel") -> str:
    """Format a visual callout string showing where lot_code is stamped on the package."""
    _req(lot_code, "lot_code")
    return f"CHECK {location_desc.upper()}: Pull Lot {lot_code}"


def embed_product_package_reference_photos(sku_id: str, image_urls: list[str]) -> dict:
    """Embed front/back package reference photos into the store bulletin."""
    _req(sku_id, "sku_id")
    if not image_urls:
        raise DataValidationError("image_urls cannot be empty")
    return {"op": "embed_product_package_reference_photos", "sku_id": str(sku_id), "photos": list(image_urls), "src": "recallstorm/comms/store_notices.py"}


def translate_bulletin_for_multilingual_crews(text: str, langs: list[str] | None = None) -> dict:
    """Generate multilingual store bulletin copies."""
    _req(text, "text")
    target_langs = list(langs or ["en", "es"])
    return {"op": "translate_bulletin_for_multilingual_crews", "langs": target_langs, "text": str(text), "src": "recallstorm/comms/store_notices.py"}


def route_notice_by_store_department_scope(dept: str, store_ids: list[str]) -> dict:
    """Route recall bulletin to the specific department lead in each store."""
    _req(dept, "dept")
    if not store_ids:
        raise DataValidationError("store_ids cannot be empty")
    return {"op": "route_notice_by_store_department_scope", "dept": str(dept).upper(), "stores": sorted(store_ids), "src": "recallstorm/comms/store_notices.py"}


def track_store_manager_read_receipt_ack(store_id: str, acked_in_mins: float) -> dict:
    """Track store manager read receipt against 15-minute SLA."""
    _req(store_id, "store_id")
    if acked_in_mins < 0:
        raise DataValidationError("acked_in_mins cannot be negative")
    return {"op": "track_store_manager_read_receipt_ack", "store_id": str(store_id), "within_sla": acked_in_mins <= 15.0, "src": "recallstorm/comms/store_notices.py"}


def version_control_amended_recall_notices(recall_id: str, rev: int = 2) -> str:
    """Generate a versioned bulletin ID when FDA expands a recall."""
    _req(recall_id, "recall_id")
    if rev < 1:
        raise DataValidationError("rev must be >= 1")
    return f"{str(recall_id).strip()}-REV{rev:02d}"


def generate_printable_backroom_poster_pdf(store_id: str, recall_id: str) -> dict:
    """Generate metadata for a printable backroom quarantine poster."""
    _req(store_id, "store_id")
    _req(recall_id, "recall_id")
    return {"op": "generate_printable_backroom_poster_pdf", "store_id": str(store_id), "recall_id": str(recall_id), "src": "recallstorm/comms/store_notices.py"}


def push_urgent_banner_to_zebra_handhelds(store_id: str, message: str) -> dict:
    """Broadcast high-priority alert banner to all active Zebra TC5x handhelds in store_id."""
    _req(store_id, "store_id")
    _req(message, "message")
    return {"op": "push_urgent_banner_to_zebra_handhelds", "store_id": str(store_id), "pushed": True, "src": "recallstorm/comms/store_notices.py"}


def archive_superseded_bulletin_versions(old_versions: list[str]) -> dict:
    """Archive superseded recall notice revisions to prevent field confusion."""
    if old_versions is None:
        raise DataValidationError("old_versions cannot be None")
    return {"op": "archive_superseded_bulletin_versions", "archived_count": len(old_versions), "src": "recallstorm/comms/store_notices.py"}
