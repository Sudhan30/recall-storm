"""FIFO rotation audits and infant formula / OTC hard expiration sweeps."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class RotationComplianceAudit:
    """FIFO / FEFO shelf stock rotation compliance audit."""

    ref_id: str = "DATE-ROT-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class ExpiredStockSweep:
    """Store sweep for expired infant formula, OTC drugs, and perishable foods."""

    ref_id: str = "DATE-SWP-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def generate_random_aisle_date_walk(store_id: str, aisles: list[str]) -> dict:
    """Generate a store date-code audit walk across aisles."""
    _req(store_id, "store_id")
    if not aisles:
        raise DataValidationError("aisles cannot be empty")
    return {"op": "generate_random_aisle_date_walk", "store_id": str(store_id), "aisles": sorted(aisles), "src": "recallstorm/food_safety/date_code_audits.py"}


def calculate_close_dated_shrink_risk(units: int, unit_cost: float, days_left: int) -> float:
    """Calculate expected shrink value for close-dated inventory."""
    if units < 0 or unit_cost < 0:
        raise DataValidationError("Negative units or unit_cost")
    factor = 1.0 if days_left <= 0 else (0.5 if days_left <= 3 else 0.1)
    return round(units * unit_cost * factor, 2)


def flag_fifo_rotation_violations(front_date_iso: str, back_date_iso: str) -> dict:
    """Flag FEFO violation when front facing expires AFTER back facing (newer stock placed in front of older stock)."""
    _req(front_date_iso, "front_date_iso")
    _req(back_date_iso, "back_date_iso")
    violation = str(front_date_iso) > str(back_date_iso)
    return {"op": "flag_fifo_rotation_violations", "violation": violation, "src": "recallstorm/food_safety/date_code_audits.py"}


def verify_infant_formula_hard_pull(sku_id: str, use_by_iso: str, today_iso: str = "2026-12-30") -> dict:
    """Enforce mandatory hard pull on infant formula at or past its FDA Use-By date."""
    _req(sku_id, "sku_id")
    _req(use_by_iso, "use_by_iso")
    pull = str(use_by_iso) <= str(today_iso)
    return {"op": "verify_infant_formula_hard_pull", "sku_id": str(sku_id), "pull_immediately": pull, "src": "recallstorm/food_safety/date_code_audits.py"}


def check_otc_drug_expiration_window(sku_id: str, days_until_expiry: int, min_days: int = 30) -> dict:
    """Check if OTC drug is within the 30-day pre-expiration pull window."""
    _req(sku_id, "sku_id")
    return {"op": "check_otc_drug_expiration_window", "sku_id": str(sku_id), "pull": int(days_until_expiry) < int(min_days), "src": "recallstorm/food_safety/date_code_audits.py"}


def score_department_freshness_index(checked: int, expired_found: int) -> float:
    """Compute department freshness compliance score in [0.0, 100.0]."""
    if checked <= 0 or expired_found < 0 or expired_found > checked:
        raise DataValidationError("Invalid checked or expired_found counts")
    return round(((checked - expired_found) / checked) * 100.0, 2)


def identify_chronic_overstock_skus(turnover_days: dict[str, int], max_shelf_life: int = 30) -> list[str]:
    """Identify SKUs whose inventory days-of-supply exceed max_shelf_life."""
    if turnover_days is None or max_shelf_life <= 0:
        raise DataValidationError("Invalid turnover_days")
    return sorted(sku for sku, days in turnover_days.items() if int(days) > max_shelf_life)


def schedule_markdown_before_expiry(sku_id: str, days_left: int) -> dict:
    """Schedule CVP markdown when 1 <= days_left <= 3."""
    _req(sku_id, "sku_id")
    eligible = 1 <= int(days_left) <= 3
    return {"op": "schedule_markdown_before_expiry", "sku_id": str(sku_id), "cvp_eligible": eligible, "src": "recallstorm/food_safety/date_code_audits.py"}


def track_associate_rotation_velocity(associate_id: str, facings_checked: int, minutes: float) -> float:
    """Compute facings audited per minute."""
    _req(associate_id, "associate_id")
    if facings_checked < 0 or minutes <= 0:
        raise DataValidationError("Invalid facings_checked or minutes")
    return round(facings_checked / minutes, 2)


def export_expired_pull_log(store_id: str, pulled_units: int) -> dict:
    """Export expired stock pull log for store_id."""
    _req(store_id, "store_id")
    if pulled_units < 0:
        raise DataValidationError("pulled_units cannot be negative")
    return {"op": "export_expired_pull_log", "store_id": str(store_id), "pulled_units": int(pulled_units), "src": "recallstorm/food_safety/date_code_audits.py"}
