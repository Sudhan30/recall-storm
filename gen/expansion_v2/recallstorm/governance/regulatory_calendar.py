"""Statutory effective date calendar and T-90 readiness drill scheduling."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class ComplianceDeadlineCalendar:
    """Enterprise calendar of upcoming federal and state statutory effective dates."""

    ref_id: str = "CAL-CMP-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class StatutoryPhaseInTracker:
    """Tracker for T-90, T-30, and T-7 day pre-enforcement readiness milestones."""

    ref_id: str = "CAL-PHS-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def track_ab418_ny_il_statutory_effective_dates() -> dict[str, str]:
    """Return canonical statutory effective dates for major food additive rules."""
    return {
        "CA_AB418": "2027-01-01",
        "FDA_RED3_FOOD": "2027-01-15",
        "FDA_RED3_DRUG": "2028-01-18",
        "IL_SB2637": "2028-01-01",
    }


def schedule_t_minus_90_day_readiness_drills(effective_date_iso: str, days_before: int = 90) -> str:
    """Compute the T-minus-90-day readiness drill date prior to effective_date_iso."""
    _req(effective_date_iso, "effective_date_iso")
    if days_before <= 0:
        raise DataValidationError("days_before must be positive")
    dt = date.fromisoformat(str(effective_date_iso)[:10]) - timedelta(days=int(days_before))
    return dt.isoformat()


def alert_merchandising_to_sell_through_cutoffs(rule_id: str, days_remaining: int) -> dict:
    """Alert buyers to stop inbound POs when days_remaining <= 60."""
    _req(rule_id, "rule_id")
    if days_remaining < 0:
        raise DataValidationError("days_remaining cannot be negative")
    return {"op": "alert_merchandising_to_sell_through_cutoffs", "rule_id": str(rule_id), "stop_pos_now": days_remaining <= 60, "src": "recallstorm/governance/regulatory_calendar.py"}


def monitor_state_legislature_amendment_feeds(state: str, bill_id: str) -> dict:
    """Track state legislature food/consumer-product bill amendments."""
    _req(state, "state")
    _req(bill_id, "bill_id")
    return {"op": "monitor_state_legislature_amendment_feeds", "state": str(state).upper(), "bill_id": str(bill_id), "src": "recallstorm/governance/regulatory_calendar.py"}


def sync_regulatory_milestones_to_corp_calendar(milestones: list[dict]) -> dict:
    """Sync statutory milestones to the corporate compliance calendar."""
    if milestones is None:
        raise DataValidationError("milestones cannot be None")
    return {"op": "sync_regulatory_milestones_to_corp_calendar", "synced_count": len(milestones), "src": "recallstorm/governance/regulatory_calendar.py"}


def calculate_working_days_to_mandatory_ban(start_date_iso: str, ban_date_iso: str) -> int:
    """Calculate Monday-Friday working days between start_date_iso and ban_date_iso."""
    _req(start_date_iso, "start_date_iso")
    _req(ban_date_iso, "ban_date_iso")
    d1 = date.fromisoformat(str(start_date_iso)[:10])
    d2 = date.fromisoformat(str(ban_date_iso)[:10])
    if d2 < d1:
        raise DataValidationError("ban_date_iso precedes start_date_iso")
    cur = d1
    workdays = 0
    while cur < d2:
        if cur.weekday() < 5:
            workdays += 1
        cur += timedelta(days=1)
    return workdays


def trigger_pre_enforcement_store_sweep_tasks(rule_id: str, hours_before_ban: int = 24) -> dict:
    """Trigger pre-enforcement store shelf sweep tasks hours_before_ban."""
    _req(rule_id, "rule_id")
    if hours_before_ban <= 0:
        raise DataValidationError("hours_before_ban must be positive")
    return {"op": "trigger_pre_enforcement_store_sweep_tasks", "rule_id": str(rule_id), "hours_before_ban": int(hours_before_ban), "src": "recallstorm/governance/regulatory_calendar.py"}


def track_fda_fsma_204_traceability_deadlines(category: str) -> dict:
    """Return FSMA Section 204 Food Traceability List compliance status for category."""
    _req(category, "category")
    return {"op": "track_fda_fsma_204_traceability_deadlines", "category": str(category), "kde_cte_required": True, "src": "recallstorm/governance/regulatory_calendar.py"}


def assign_executive_owners_to_upcoming_laws(law_id: str, owner_id: str) -> dict:
    """Assign an executive owner to an upcoming statutory mandate."""
    _req(law_id, "law_id")
    _req(owner_id, "owner_id")
    return {"op": "assign_executive_owners_to_upcoming_laws", "law_id": str(law_id), "owner_id": str(owner_id), "src": "recallstorm/governance/regulatory_calendar.py"}


def generate_twelve_month_regulatory_horizon_map(year: int = 2027) -> dict:
    """Generate a 12-month regulatory horizon map."""
    if year < 2020:
        raise DataValidationError("Invalid year")
    return {"op": "generate_twelve_month_regulatory_horizon_map", "year": int(year), "laws": track_ab418_ny_il_statutory_effective_dates(), "src": "recallstorm/governance/regulatory_calendar.py"}
