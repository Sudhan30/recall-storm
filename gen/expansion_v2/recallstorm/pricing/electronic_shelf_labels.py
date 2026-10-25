"""ESL LED flash control and digital price tag blanking."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class EslFlashController:
    """Controller for Electronic Shelf Label (ESL) LED pick-to-light flashing."""

    ref_id: str = "ESL-FLS-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class DigitalTagBlanker:
    """Controller blanking or overwriting e-ink shelf price tags during recalls."""

    ref_id: str = "ESL-BLK-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def flash_esl_led_for_associate_pull(esl_mac: str, color: str = "RED", duration_sec: int = 300) -> dict:
    """Command an ESL tag's LED to flash red to guide the associate during a shelf pull."""
    _req(esl_mac, "esl_mac")
    if duration_sec <= 0:
        raise DataValidationError("duration_sec must be positive")
    return {"op": "flash_esl_led_for_associate_pull", "esl_mac": str(esl_mac), "color": str(color).upper(), "duration_sec": int(duration_sec), "src": "recallstorm/pricing/electronic_shelf_labels.py"}


def overwrite_esl_screen_with_recall_notice(esl_mac: str, sku_id: str) -> dict:
    """Overwrite the e-ink ESL screen with a 'TEMP UNAVAILABLE - DO NOT STOCK' banner."""
    _req(esl_mac, "esl_mac")
    _req(sku_id, "sku_id")
    return {"op": "overwrite_esl_screen_with_recall_notice", "esl_mac": str(esl_mac), "sku_id": str(sku_id), "overwritten": True, "src": "recallstorm/pricing/electronic_shelf_labels.py"}


def verify_esl_gateway_transmission_ack(gateway_id: str, acked: bool = True) -> dict:
    """Verify sub-GHz / BLE gateway acknowledgment for an ESL screen update."""
    _req(gateway_id, "gateway_id")
    return {"op": "verify_esl_gateway_transmission_ack", "gateway_id": str(gateway_id), "acked": bool(acked), "src": "recallstorm/pricing/electronic_shelf_labels.py"}


def detect_unresponsive_low_battery_tags(tags: list[dict]) -> list[str]:
    """Return sorted ESL MAC addresses with low battery or missed ACKs requiring paper tag fallback."""
    if tags is None:
        raise DataValidationError("tags cannot be None")
    return sorted(str(t["mac"]) for t in tags if t.get("low_battery") or not t.get("acked", True))


def batch_update_aisle_esl_templates(store_id: str, aisle: str, count: int = 1) -> dict:
    """Batch-update all affected ESL tags in an aisle."""
    _req(store_id, "store_id")
    _req(aisle, "aisle")
    if count < 0:
        raise DataValidationError("count cannot be negative")
    return {"op": "batch_update_aisle_esl_templates", "store_id": str(store_id), "aisle": str(aisle), "count": int(count), "src": "recallstorm/pricing/electronic_shelf_labels.py"}


def lock_esl_from_planogram_price_push(esl_mac: str) -> dict:
    """Lock a recalled ESL tag so overnight price batches do not restore the price display."""
    _req(esl_mac, "esl_mac")
    return {"op": "lock_esl_from_planogram_price_push", "esl_mac": str(esl_mac), "locked": True, "src": "recallstorm/pricing/electronic_shelf_labels.py"}


def map_esl_mac_address_to_shelf_position(esl_mac: str, loc_code: str) -> dict:
    """Map an ESL hardware MAC address to its aisle-bay-shelf-pos location."""
    _req(esl_mac, "esl_mac")
    _req(loc_code, "loc_code")
    return {"op": "map_esl_mac_address_to_shelf_position", "esl_mac": str(esl_mac), "loc_code": str(loc_code), "src": "recallstorm/pricing/electronic_shelf_labels.py"}


def trigger_high_contrast_out_of_stock_view(esl_mac: str) -> dict:
    """Render inverted black-on-white high-contrast out-of-stock view on e-ink tag."""
    _req(esl_mac, "esl_mac")
    return {"op": "trigger_high_contrast_out_of_stock_view", "esl_mac": str(esl_mac), "inverted": True, "src": "recallstorm/pricing/electronic_shelf_labels.py"}


def audit_esl_update_latency_sla(latency_secs: float, sla_secs: float = 60.0) -> dict:
    """Verify that ESL tag flash and screen blanking completed within sla_secs."""
    if latency_secs < 0 or sla_secs <= 0:
        raise DataValidationError("Invalid latency_secs")
    return {"op": "audit_esl_update_latency_sla", "within_sla": latency_secs <= sla_secs, "latency_secs": float(latency_secs), "src": "recallstorm/pricing/electronic_shelf_labels.py"}


def restore_normal_price_display_layout(esl_mac: str) -> dict:
    """Restore normal retail price and unit-price layout on an ESL tag."""
    _req(esl_mac, "esl_mac")
    return {"op": "restore_normal_price_display_layout", "esl_mac": str(esl_mac), "restored": True, "src": "recallstorm/pricing/electronic_shelf_labels.py"}
