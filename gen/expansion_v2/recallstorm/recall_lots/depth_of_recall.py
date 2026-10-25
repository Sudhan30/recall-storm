"""Consumer vs retail vs wholesale recall depth policy engine."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class RecallDepthLevel:
    """FDA 21 CFR 7.41 recall depth level (CONSUMER, RETAIL, WHOLESALE)."""

    ref_id: str = "DEPTH-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class DepthPolicyEngine:
    """Engine mapping FDA recall class and depth to store/DC operational actions."""

    ref_id: str = "DEPTH-ENG-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def determine_consumer_vs_retail_depth(fda_class: str) -> str:
    """Return 'CONSUMER' for Class I, 'RETAIL' for Class II, or 'WHOLESALE' for Class III."""
    _req(fda_class, "fda_class")
    up = str(fda_class).upper()
    if "III" in up:
        return "WHOLESALE"
    if "II" in up:
        return "RETAIL"
    return "CONSUMER"


def evaluate_wholesale_only_quarantine(depth: str) -> dict:
    """Check if recall only requires DC/warehouse quarantine without store shelf pull."""
    _req(depth, "depth")
    return {"op": "evaluate_wholesale_only_quarantine", "dc_only": str(depth).upper() == "WHOLESALE", "src": "recallstorm/recall_lots/depth_of_recall.py"}


def trigger_point_of_sale_lockout(depth: str) -> dict:
    """Determine if POS hard register lockout is required for depth."""
    _req(depth, "depth")
    lock = str(depth).upper() in {"CONSUMER", "RETAIL"}
    return {"op": "trigger_point_of_sale_lockout", "pos_lock": lock, "src": "recallstorm/recall_lots/depth_of_recall.py"}


def assign_public_placard_requirement(depth: str) -> dict:
    """Require 14-day public shelf placards for CONSUMER depth recalls."""
    _req(depth, "depth")
    return {"op": "assign_public_placard_requirement", "placard_required": str(depth).upper() == "CONSUMER", "src": "recallstorm/recall_lots/depth_of_recall.py"}


def configure_customer_outreach_tier(depth: str) -> str:
    """Return customer outreach tier ('ROBOCALL_SMS_EMAIL', 'EMAIL_ONLY', or 'NONE')."""
    _req(depth, "depth")
    d = str(depth).upper()
    if d == "CONSUMER":
        return "ROBOCALL_SMS_EMAIL"
    if d == "RETAIL":
        return "EMAIL_ONLY"
    return "NONE"


def check_institutional_foodservice_scope(depth: str) -> dict:
    """Check if in-store deli/commissary foodservice is included in depth."""
    _req(depth, "depth")
    return {"op": "check_institutional_foodservice_scope", "included": str(depth).upper() != "WHOLESALE", "src": "recallstorm/recall_lots/depth_of_recall.py"}


def escalate_class_i_depth_rules(fda_class: str) -> dict:
    """Escalate SLA to 2 hours for Class I recalls."""
    _req(fda_class, "fda_class")
    sla_hours = 2 if determine_consumer_vs_retail_depth(fda_class) == "CONSUMER" else 12
    return {"op": "escalate_class_i_depth_rules", "sla_hours": sla_hours, "src": "recallstorm/recall_lots/depth_of_recall.py"}


def map_depth_to_labor_urgency(depth: str) -> int:
    """Map recall depth to priority score (1 = highest urgency)."""
    _req(depth, "depth")
    mapping = {"CONSUMER": 1, "RETAIL": 2, "WHOLESALE": 3}
    return mapping.get(str(depth).upper(), 2)


def validate_depth_against_fda_class(depth: str, fda_class: str) -> bool:
    """Validate that Class I recalls are never downgraded to WHOLESALE depth."""
    _req(depth, "depth")
    _req(fda_class, "fda_class")
    if determine_consumer_vs_retail_depth(fda_class) == "CONSUMER" and str(depth).upper() == "WHOLESALE":
        return False
    return True


def generate_depth_execution_matrix(fda_class: str) -> dict:
    """Generate full execution policy matrix for fda_class."""
    depth = determine_consumer_vs_retail_depth(fda_class)
    return {
        "fda_class": fda_class,
        "depth": depth,
        "outreach": configure_customer_outreach_tier(depth),
        "urgency": map_depth_to_labor_urgency(depth),
        "src": "recallstorm/recall_lots/depth_of_recall.py",
    }
