"""Foodborne illness complaint clustering and precautionary lot holds."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class IllnessComplaintTicket:
    """Consumer foodborne illness or injury complaint ticket."""

    ref_id: str = "CMP-TKT-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class ClusterSignalDetector:
    """Epidemiological cluster signal detector across stores and lots."""

    ref_id: str = "CMP-SIG-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def ingest_call_center_symptom_log(ticket_id: str, symptoms: list[str]) -> dict:
    """Ingest a consumer symptom log from the contact center."""
    _req(ticket_id, "ticket_id")
    if not symptoms:
        raise DataValidationError("symptoms cannot be empty")
    return {"op": "ingest_call_center_symptom_log", "ticket_id": str(ticket_id), "symptoms": sorted(symptoms), "src": "recallstorm/food_safety/consumer_complaints.py"}


def calculate_incubation_period_match(onset_hours: float, pathogen: str = "SALMONELLA") -> dict:
    """Check if symptom onset_hours matches typical pathogen incubation window (6-72h for Salmonella)."""
    if onset_hours < 0:
        raise DataValidationError("onset_hours cannot be negative")
    p = str(pathogen).upper()
    if p == "SALMONELLA":
        matched = 6.0 <= onset_hours <= 72.0
    elif p == "STAPH":
        matched = 0.5 <= onset_hours <= 8.0
    else:
        matched = onset_hours <= 168.0
    return {"op": "calculate_incubation_period_match", "pathogen": p, "matched": matched, "src": "recallstorm/food_safety/consumer_complaints.py"}


def detect_geographic_complaint_cluster(complaints_by_store: dict[str, int], threshold: int = 3) -> list[str]:
    """Return store_ids where complaint count meets or exceeds threshold."""
    if complaints_by_store is None or threshold <= 0:
        raise DataValidationError("Invalid cluster parameters")
    return sorted(st for st, cnt in complaints_by_store.items() if int(cnt) >= threshold)


def link_loyalty_card_purchase_lot(loyalty_id: str, sku_id: str, lot_id: str = "L2601") -> dict:
    """Link a customer loyalty receipt to the probable lot on shelf at purchase time."""
    _req(loyalty_id, "loyalty_id")
    _req(sku_id, "sku_id")
    return {"op": "link_loyalty_card_purchase_lot", "loyalty_id": str(loyalty_id), "sku_id": str(sku_id), "lot_id": str(lot_id), "src": "recallstorm/food_safety/consumer_complaints.py"}


def escalate_hospitalization_report(ticket_id: str, hospitalized: bool = True) -> dict:
    """Escalate any complaint involving hospitalization or ER visit to VP Food Safety."""
    _req(ticket_id, "ticket_id")
    return {"op": "escalate_hospitalization_report", "ticket_id": str(ticket_id), "priority": "CRITICAL" if hospitalized else "STANDARD", "src": "recallstorm/food_safety/consumer_complaints.py"}


def check_foreign_material_photo_hash(image_bytes: bytes | str) -> str:
    """Compute SHA-256 hash of a customer-submitted foreign material photo to detect duplicate fraud."""
    _req(image_bytes, "image_bytes")
    raw = image_bytes.encode("utf-8") if isinstance(image_bytes, str) else bytes(image_bytes)
    return hashlib.sha256(raw).hexdigest()[:16]


def cross_reference_iwaspoisoned_feed(store_id: str, reports: int = 0) -> dict:
    """Cross-reference crowd-sourced foodborne illness feeds for store_id."""
    _req(store_id, "store_id")
    if reports < 0:
        raise DataValidationError("reports cannot be negative")
    return {"op": "cross_reference_iwaspoisoned_feed", "store_id": str(store_id), "alert": reports >= 2, "src": "recallstorm/food_safety/consumer_complaints.py"}


def trigger_precautionary_lot_hold(sku_id: str, lot_id: str) -> dict:
    """Trigger an internal precautionary hold on a lot while lab testing is pending."""
    _req(sku_id, "sku_id")
    _req(lot_id, "lot_id")
    return {"op": "trigger_precautionary_lot_hold", "sku_id": str(sku_id), "lot_id": str(lot_id), "status": "HOLD_VERIFY", "src": "recallstorm/food_safety/consumer_complaints.py"}


def generate_fda_medwatch_draft(ticket_id: str, sku_id: str) -> dict:
    """Generate an FDA MedWatch / CAERS adverse event report draft."""
    _req(ticket_id, "ticket_id")
    _req(sku_id, "sku_id")
    return {"op": "generate_fda_medwatch_draft", "ticket_id": str(ticket_id), "sku_id": str(sku_id), "src": "recallstorm/food_safety/consumer_complaints.py"}


def track_sample_retrieval_courier(ticket_id: str, tracking_no: str) -> dict:
    """Track refrigerated courier retrieving leftover product sample from consumer's home."""
    _req(ticket_id, "ticket_id")
    _req(tracking_no, "tracking_no")
    return {"op": "track_sample_retrieval_courier", "ticket_id": str(ticket_id), "tracking_no": str(tracking_no), "src": "recallstorm/food_safety/consumer_complaints.py"}
