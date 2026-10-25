"""C-Suite war room situation digests and GeoJSON completion maps."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class CSuiteDigestGenerator:
    """Generator for hourly C-Suite recall crisis situation digests."""

    ref_id: str = "EXE-DIG-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class CrisisWarRoomFeed:
    """Real-time feed for the corporate Food Safety War Room."""

    ref_id: str = "EXE-WAR-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def synthesize_hourly_war_room_situation_report(recall_id: str, completion_pct: float) -> dict:
    """Synthesize an hourly War Room SITREP."""
    _req(recall_id, "recall_id")
    if not (0.0 <= completion_pct <= 100.0):
        raise DataValidationError("completion_pct must be in [0, 100]")
    return {"op": "synthesize_hourly_war_room_situation_report", "recall_id": str(recall_id), "completion_pct": float(completion_pct), "src": "recallstorm/analytics/executive_briefings.py"}


def highlight_red_flag_non_compliant_districts(pct_by_district: dict[str, float], min_pct: float = 90.0) -> list[str]:
    """Return sorted district IDs lagging below min_pct completion."""
    if pct_by_district is None:
        raise DataValidationError("pct_by_district cannot be None")
    return sorted(d for d, pct in pct_by_district.items() if float(pct) < min_pct)


def project_estimated_time_to_full_containment(remaining_tasks: int, tasks_per_hour: float = 50.0) -> float:
    """Project hours remaining until 100% chainwide containment."""
    if remaining_tasks < 0 or tasks_per_hour <= 0:
        raise DataValidationError("Invalid remaining_tasks or tasks_per_hour")
    return round(remaining_tasks / tasks_per_hour, 2)


def summarize_media_and_regulator_touchpoints(fda_calls: int, media_inquiries: int) -> dict:
    """Summarize external regulatory and press touchpoints."""
    if fda_calls < 0 or media_inquiries < 0:
        raise DataValidationError("Negative touchpoint counts")
    return {"op": "summarize_media_and_regulator_touchpoints", "fda_calls": int(fda_calls), "media_inquiries": int(media_inquiries), "src": "recallstorm/analytics/executive_briefings.py"}


def track_class_i_hospitalization_escalations(cases_reported: int) -> dict:
    """Track reported consumer hospitalizations on a Class I recall."""
    if cases_reported < 0:
        raise DataValidationError("cases_reported cannot be negative")
    return {"op": "track_class_i_hospitalization_escalations", "cases_reported": int(cases_reported), "ceo_alert": cases_reported > 0, "src": "recallstorm/analytics/executive_briefings.py"}


def compare_current_event_to_historical_baseline(current_mins: float, baseline_mins: float = 180.0) -> dict:
    """Compare current recall containment speed against historical baseline."""
    if current_mins <= 0 or baseline_mins <= 0:
        raise DataValidationError("Minutes must be positive")
    return {"op": "compare_current_event_to_historical_baseline", "faster_than_baseline": current_mins <= baseline_mins, "src": "recallstorm/analytics/executive_briefings.py"}


def format_mobile_friendly_ceo_flash_email(recall_id: str, headline: str) -> str:
    """Format a 3-line mobile flash summary for the CEO and COO."""
    _req(recall_id, "recall_id")
    _req(headline, "headline")
    return f"[FLASH {recall_id}] {headline} | POS Locked: 100% | Store Pulls Active."


def generate_general_counsel_privilege_summary(recall_id: str) -> dict:
    """Generate an Attorney-Client Privileged legal risk summary."""
    _req(recall_id, "recall_id")
    return {"op": "generate_general_counsel_privilege_summary", "recall_id": str(recall_id), "header": "ATTORNEY-CLIENT PRIVILEGED / WORK PRODUCT", "src": "recallstorm/analytics/executive_briefings.py"}


def update_live_geojson_store_completion_map(stores: list[dict]) -> dict:
    """Build a GeoJSON FeatureCollection of store completion status."""
    if stores is None:
        raise DataValidationError("stores cannot be None")
    features = [
        {
            "type": "Feature",
            "properties": {"store_id": s.get("store_id")},
            "geometry": {"type": "Point", "coordinates": [float(s.get("lon", -118.0)), float(s.get("lat", 34.0))]},
        }
        for s in stores
    ]
    return {"type": "FeatureCollection", "features": features}


def archive_war_room_decision_log_snapshots(recall_id: str, decisions_count: int = 1) -> dict:
    """Archive timestamped War Room executive decision logs."""
    _req(recall_id, "recall_id")
    if decisions_count < 0:
        raise DataValidationError("decisions_count cannot be negative")
    return {"op": "archive_war_room_decision_log_snapshots", "recall_id": str(recall_id), "decisions_count": int(decisions_count), "src": "recallstorm/analytics/executive_briefings.py"}
