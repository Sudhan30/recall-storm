"""Loyalty household purchase queries and automated Class I outreach."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class LoyaltyRecallOutreach:
    """Outreach campaign targeting loyalty households that purchased a recalled UPC."""

    ref_id: str = "OUT-LOY-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class AutomatedCustomerAlert:
    """Multi-channel (email, SMS, robocall, app push) customer safety alert."""

    ref_id: str = "OUT-ALT-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def query_loyalty_households_by_upc_window(purchases: list[dict], upc: str) -> list[str]:
    """Return sorted household_ids that purchased upc."""
    if purchases is None:
        raise DataValidationError("purchases cannot be None")
    _req(upc, "upc")
    return sorted({str(p["household_id"]) for p in purchases if p.get("upc") == upc})


def filter_online_delivery_order_histories(orders: list[dict], sku_id: str) -> list[str]:
    """Return order_ids from online delivery histories containing sku_id."""
    if orders is None:
        raise DataValidationError("orders cannot be None")
    _req(sku_id, "sku_id")
    return [str(o["order_id"]) for o in orders if sku_id in o.get("skus", [])]


def send_personalized_email_sms_recall_alert(household_id: str, sku_name: str, store_id: str) -> dict:
    """Format a personalized customer recall notification citing purchase store and item."""
    _req(household_id, "household_id")
    _req(sku_name, "sku_name")
    _req(store_id, "store_id")
    return {"op": "send_personalized_email_sms_recall_alert", "household_id": str(household_id), "sku_name": str(sku_name), "store_id": str(store_id), "sent": True, "src": "recallstorm/comms/customer_notifications.py"}


def trigger_automated_robocall_for_class_i(household_ids: list[str], recall_id: str) -> dict:
    """Trigger automated voice robocalls for life-threatening Class I recalls (TCPA emergency exemption)."""
    if not household_ids:
        raise DataValidationError("household_ids cannot be empty")
    _req(recall_id, "recall_id")
    return {"op": "trigger_automated_robocall_for_class_i", "recall_id": str(recall_id), "calls_queued": len(household_ids), "src": "recallstorm/comms/customer_notifications.py"}


def provide_self_service_lot_checker_url(recall_id: str, gtin: str) -> str:
    """Build a customer self-service web URL to check package lot codes."""
    _req(recall_id, "recall_id")
    _req(gtin, "gtin")
    return f"https://recalls.retailer.example/check/{str(recall_id).strip()}/{str(gtin).strip()}"


def track_email_bounce_and_open_metrics(sent: int, bounced: int, opened: int) -> dict:
    """Compute email delivery and open rates for regulatory effectiveness reporting."""
    if sent <= 0 or bounced < 0 or opened < 0 or bounced > sent or opened > sent:
        raise DataValidationError("Invalid email metrics")
    delivered = sent - bounced
    open_rate = (opened / delivered) if delivered > 0 else 0.0
    return {"op": "track_email_bounce_and_open_metrics", "delivered": delivered, "open_rate": round(open_rate, 4), "src": "recallstorm/comms/customer_notifications.py"}


def log_opt_out_safety_override_justification(household_id: str, fda_class: str = "Class I") -> dict:
    """Log statutory public-health override justification when contacting marketing-opted-out customers."""
    _req(household_id, "household_id")
    return {"op": "log_opt_out_safety_override_justification", "household_id": str(household_id), "basis": f"PUBLIC_SAFETY_{fda_class}", "src": "recallstorm/comms/customer_notifications.py"}


def generate_app_push_notification_payload(household_id: str, title: str) -> dict:
    """Generate mobile app push notification payload."""
    _req(household_id, "household_id")
    _req(title, "title")
    return {"op": "generate_app_push_notification_payload", "household_id": str(household_id), "title": str(title), "src": "recallstorm/comms/customer_notifications.py"}


def handle_inbound_customer_reply_routing(reply_text: str) -> str:
    """Route inbound SMS/email customer replies ('ILLNESS_ESCALATION' or 'REFUND_INFO')."""
    _req(reply_text, "reply_text")
    low = str(reply_text).lower()
    if any(k in low for k in ("sick", "hospital", "doctor", "ill", "reaction", "allergy")):
        return "ILLNESS_ESCALATION"
    return "REFUND_INFO"


def generate_outreach_effectiveness_summary(notified: int, returned_units: int) -> dict:
    """Summarize customer outreach effectiveness."""
    if notified < 0 or returned_units < 0:
        raise DataValidationError("Negative outreach counts")
    return {"op": "generate_outreach_effectiveness_summary", "notified": int(notified), "returned_units": int(returned_units), "src": "recallstorm/comms/customer_notifications.py"}
