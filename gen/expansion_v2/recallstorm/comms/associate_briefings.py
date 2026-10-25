"""5-minute shift huddle scripts and badge attendance tracking."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class ShiftHuddleScript:
    """5-minute pre-shift associate huddle script."""

    ref_id: str = "HUD-SCR-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class AssociateBriefingTracker:
    """Tracker for associate huddle badge-scan attendance."""

    ref_id: str = "HUD-TRK-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def generate_five_minute_huddle_talking_points(recall_id: str, sku_names: list[str]) -> list[str]:
    """Generate 3 concise talking points for the overnight shift huddle."""
    _req(recall_id, "recall_id")
    if not sku_names:
        raise DataValidationError("sku_names cannot be empty")
    return [
        f"Recall {recall_id}: Pull {', '.join(sku_names)} before deadline.",
        "Check endcaps, topstock, and online pickup totes.",
        "Stage pulled cases in locked backroom quarantine cage.",
    ]


def customize_script_for_front_end_cashiers(recall_id: str) -> str:
    """Generate front-end cashier briefing instructions."""
    _req(recall_id, "recall_id")
    return f"Cashiers ({recall_id}): If a register stop-sale alert triggers, apologize, retain the item in the quarantine bin, and offer an equal-price substitute."


def build_deli_bakery_prep_safety_brief(dept: str, allergen_or_additive: str) -> dict:
    """Build a fresh-department prep safety brief."""
    _req(dept, "dept")
    _req(allergen_or_additive, "allergen_or_additive")
    return {"op": "build_deli_bakery_prep_safety_brief", "dept": str(dept).upper(), "hazard": str(allergen_or_additive), "src": "recallstorm/comms/associate_briefings.py"}


def quiz_associate_on_lot_code_location(selected_answer: str, correct_answer: str) -> dict:
    """Score a 1-question handheld verification quiz before an associate starts a lot pull."""
    _req(selected_answer, "selected_answer")
    _req(correct_answer, "correct_answer")
    passed = str(selected_answer).strip().upper() == str(correct_answer).strip().upper()
    return {"op": "quiz_associate_on_lot_code_location", "passed": passed, "src": "recallstorm/comms/associate_briefings.py"}


def record_huddle_attendance_badge_scans(store_id: str, badge_ids: list[str]) -> dict:
    """Record associate badge scans at the pre-shift recall huddle."""
    _req(store_id, "store_id")
    if not badge_ids:
        raise DataValidationError("badge_ids cannot be empty")
    return {"op": "record_huddle_attendance_badge_scans", "store_id": str(store_id), "count": len(set(badge_ids)), "src": "recallstorm/comms/associate_briefings.py"}


def provide_customer_de_escalation_phrases(lang: str = "en") -> list[str]:
    """Return approved customer service de-escalation phrases."""
    _req(lang, "lang")
    return [
        "For your safety, this item is subject to a regulatory recall.",
        "We are happy to provide a full refund or an equal-price substitute immediately.",
    ]


def highlight_gloves_ppe_handling_rules(hazard_type: str) -> dict:
    """Specify PPE requirements when pulling leaking or chemical products."""
    _req(hazard_type, "hazard_type")
    ppe = ["NITRILE_GLOVES", "GOGGLES"] if "caustic" in str(hazard_type).lower() else ["GLOVES"]
    return {"op": "highlight_gloves_ppe_handling_rules", "ppe": ppe, "src": "recallstorm/comms/associate_briefings.py"}


def update_breakroom_digital_signage_feed(store_id: str, slide_id: str) -> dict:
    """Push recall awareness slide to associate breakroom screens."""
    _req(store_id, "store_id")
    _req(slide_id, "slide_id")
    return {"op": "update_breakroom_digital_signage_feed", "store_id": str(store_id), "slide_id": str(slide_id), "src": "recallstorm/comms/associate_briefings.py"}


def track_unbriefed_scheduled_associates(scheduled: list[str], briefed: set[str]) -> list[str]:
    """Return sorted associate IDs on shift who have not yet acknowledged the recall briefing."""
    if scheduled is None or briefed is None:
        raise DataValidationError("Inputs cannot be None")
    return sorted(set(scheduled) - set(briefed))


def export_training_compliance_log(store_id: str, briefed_count: int) -> dict:
    """Export associate briefing compliance log."""
    _req(store_id, "store_id")
    if briefed_count < 0:
        raise DataValidationError("briefed_count cannot be negative")
    return {"op": "export_training_compliance_log", "store_id": str(store_id), "briefed_count": int(briefed_count), "src": "recallstorm/comms/associate_briefings.py"}
