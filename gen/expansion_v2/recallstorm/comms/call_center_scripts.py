"""Contact center FAQ articles, symptom triage trees, and nurse-line routing."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError
from recallstorm.gs1.lots import lot_matches_recall


@dataclass(frozen=True)
class ContactCenterKnowledgeBase:
    """Contact center agent recall FAQ knowledge base article."""

    ref_id: str = "CC-KB-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class EscalationTriageTree:
    """Decision tree routing adverse events vs refund inquiries."""

    ref_id: str = "CC-TRI-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def publish_agent_recall_faq_article(recall_id: str, summary: str) -> dict:
    """Publish a recall FAQ article to contact center agent desktops."""
    _req(recall_id, "recall_id")
    _req(summary, "summary")
    return {"op": "publish_agent_recall_faq_article", "recall_id": str(recall_id), "summary": str(summary), "published": True, "src": "recallstorm/comms/call_center_scripts.py"}


def build_symptom_intake_decision_tree(recall_id: str) -> dict:
    """Build structured symptom-intake questions for contact center agents."""
    _req(recall_id, "recall_id")
    return {"op": "build_symptom_intake_decision_tree", "recall_id": str(recall_id), "questions": ["When consumed?", "Symptoms?", "Lot code?"], "src": "recallstorm/comms/call_center_scripts.py"}


def route_adverse_event_to_nurse_line(ticket_id: str, has_symptoms: bool = True) -> dict:
    """Warm-transfer callers reporting clinical symptoms to the 24/7 triage nurse/toxicology line."""
    _req(ticket_id, "ticket_id")
    queue = "NURSE_TOXICOLOGY_LINE" if has_symptoms else "GENERAL_REFUND_QUEUE"
    return {"op": "route_adverse_event_to_nurse_line", "ticket_id": str(ticket_id), "queue": queue, "src": "recallstorm/comms/call_center_scripts.py"}


def provide_instant_e_gift_card_issuance(customer_id: str, amount_usd: float) -> dict:
    """Issue an instant digital gift card refund to a caller."""
    _req(customer_id, "customer_id")
    if amount_usd <= 0 or amount_usd > 500.0:
        raise DataValidationError("Invalid e-gift card amount")
    return {"op": "provide_instant_e_gift_card_issuance", "customer_id": str(customer_id), "amount_usd": round(float(amount_usd), 2), "src": "recallstorm/comms/call_center_scripts.py"}


def validate_caller_reported_lot_string(caller_lot: str, recalled_lots: list[str]) -> dict:
    """Check whether the lot code read over the phone by a caller is affected."""
    _req(caller_lot, "caller_lot")
    if recalled_lots is None:
        raise DataValidationError("recalled_lots cannot be None")
    affected = lot_matches_recall(str(caller_lot), recalled_lots)
    return {"op": "validate_caller_reported_lot_string", "caller_lot": str(caller_lot), "affected": affected, "src": "recallstorm/comms/call_center_scripts.py"}


def log_media_press_inquiry_diversion(caller_org: str) -> dict:
    """Immediately divert journalist/media callers to Corporate Communications."""
    _req(caller_org, "caller_org")
    return {"op": "log_media_press_inquiry_diversion", "caller_org": str(caller_org), "diverted_to": "CORP_PR_DESK", "src": "recallstorm/comms/call_center_scripts.py"}


def update_ivr_phone_tree_announcement(recall_id: str, active: bool = True) -> dict:
    """Configure front-end IVR phone tree greeting for high-volume recalls."""
    _req(recall_id, "recall_id")
    return {"op": "update_ivr_phone_tree_announcement", "recall_id": str(recall_id), "active": bool(active), "src": "recallstorm/comms/call_center_scripts.py"}


def track_call_volume_spike_by_recall(calls_per_hour: int, baseline: int = 50) -> dict:
    """Detect call volume spikes exceeding 2x baseline."""
    if calls_per_hour < 0 or baseline <= 0:
        raise DataValidationError("Invalid call counts")
    return {"op": "track_call_volume_spike_by_recall", "spike": calls_per_hour > (baseline * 2), "calls_per_hour": int(calls_per_hour), "src": "recallstorm/comms/call_center_scripts.py"}


def sync_crm_case_tags_with_recall_id(case_id: str, recall_id: str) -> dict:
    """Tag CRM contact center cases with the canonical recall_id."""
    _req(case_id, "case_id")
    _req(recall_id, "recall_id")
    return {"op": "sync_crm_case_tags_with_recall_id", "case_id": str(case_id), "recall_id": str(recall_id), "src": "recallstorm/comms/call_center_scripts.py"}


def generate_daily_sentiment_digest(total_calls: int, escalations: int) -> dict:
    """Generate daily contact center recall digest."""
    if total_calls < 0 or escalations < 0 or escalations > total_calls:
        raise DataValidationError("Invalid call/escalation counts")
    return {"op": "generate_daily_sentiment_digest", "total_calls": int(total_calls), "escalations": int(escalations), "src": "recallstorm/comms/call_center_scripts.py"}
