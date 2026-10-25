"""PR crisis holding statements and social media complaint monitoring."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class PrCrisisStatement:
    """Corporate public relations holding statement."""

    ref_id: str = "PR-STM-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class SocialMediaMonitor:
    """Monitor for viral social media product safety complaints."""

    ref_id: str = "PR-SOC-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def draft_reactive_media_holding_statement(recall_id: str, sku_name: str) -> str:
    """Draft a reactive corporate media holding statement."""
    _req(recall_id, "recall_id")
    _req(sku_name, "sku_name")
    return (
        f"Customer safety is our top priority. Upon learning of recall {recall_id} involving {sku_name}, "
        "we immediately blocked register sales and instructed stores to remove affected inventory."
    )


def monitor_local_news_social_mentions(mentions_per_hour: int, threshold: int = 25) -> dict:
    """Flag spikes in local news or social media mentions."""
    if mentions_per_hour < 0 or threshold <= 0:
        raise DataValidationError("Invalid mention counts")
    return {"op": "monitor_local_news_social_mentions", "alert": mentions_per_hour >= threshold, "mentions": int(mentions_per_hour), "src": "recallstorm/comms/media_holding_statements.py"}


def flag_viral_tiktok_product_complaints(video_id: str, views: int) -> dict:
    """Flag viral social video complaints (> 10,000 views) for rapid QA triage."""
    _req(video_id, "video_id")
    if views < 0:
        raise DataValidationError("views cannot be negative")
    return {"op": "flag_viral_tiktok_product_complaints", "video_id": str(video_id), "viral_alert": views >= 10000, "src": "recallstorm/comms/media_holding_statements.py"}


def coordinate_trade_association_alignment(assoc_name: str, recall_id: str) -> dict:
    """Align industry messaging with retail/food trade associations (e.g. FMI)."""
    _req(assoc_name, "assoc_name")
    _req(recall_id, "recall_id")
    return {"op": "coordinate_trade_association_alignment", "assoc_name": str(assoc_name), "recall_id": str(recall_id), "src": "recallstorm/comms/media_holding_statements.py"}


def approve_corporate_website_recall_page(recall_id: str, legal_approved: bool = True) -> dict:
    """Publish recall notice to public corporate recalls web page after Legal approval."""
    _req(recall_id, "recall_id")
    return {"op": "approve_corporate_website_recall_page", "recall_id": str(recall_id), "live": bool(legal_approved), "src": "recallstorm/comms/media_holding_statements.py"}


def track_journalist_inquiry_deadlines(outlet: str, minutes_left: float) -> dict:
    """Track press inquiry response deadlines."""
    _req(outlet, "outlet")
    if minutes_left < 0:
        raise DataValidationError("minutes_left cannot be negative")
    return {"op": "track_journalist_inquiry_deadlines", "outlet": str(outlet), "urgent": minutes_left <= 60.0, "src": "recallstorm/comms/media_holding_statements.py"}


def align_statement_with_fda_release_time(our_release_iso: str, fda_release_iso: str) -> dict:
    """Verify that public statement is synchronized with FDA announcement."""
    _req(our_release_iso, "our_release_iso")
    _req(fda_release_iso, "fda_release_iso")
    return {"op": "align_statement_with_fda_release_time", "aligned": str(our_release_iso) >= str(fda_release_iso), "src": "recallstorm/comms/media_holding_statements.py"}


def brief_executive_spokesperson_q_and_a(recall_id: str, facts: list[str]) -> dict:
    """Assemble Q&A talking points for the corporate spokesperson."""
    _req(recall_id, "recall_id")
    if not facts:
        raise DataValidationError("facts cannot be empty")
    return {"op": "brief_executive_spokesperson_q_and_a", "recall_id": str(recall_id), "fact_count": len(facts), "src": "recallstorm/comms/media_holding_statements.py"}


def verify_store_no_comment_policy_reminder(store_id: str) -> dict:
    """Remind store managers to refer all press/camera crews to Corporate Media Relations."""
    _req(store_id, "store_id")
    return {"op": "verify_store_no_comment_policy_reminder", "store_id": str(store_id), "reminded": True, "src": "recallstorm/comms/media_holding_statements.py"}


def archive_public_relations_timeline(recall_id: str, events_count: int = 1) -> dict:
    """Archive timestamped PR communications timeline."""
    _req(recall_id, "recall_id")
    if events_count < 0:
        raise DataValidationError("events_count cannot be negative")
    return {"op": "archive_public_relations_timeline", "recall_id": str(recall_id), "events_count": int(events_count), "src": "recallstorm/comms/media_holding_statements.py"}
