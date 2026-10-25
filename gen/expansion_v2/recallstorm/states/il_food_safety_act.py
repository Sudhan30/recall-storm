"""Illinois SB 2637 Food Safety Act additive bans and sell-through tracking."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class IlAdditiveBanRule:
    """Domain entity for Illinois SB 2637 Food Safety Act."""

    ref_id: str = "IL-SB2637"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class IlGracePeriodTracker:
    """Tracker for Illinois statutory sell-through grace periods."""

    ref_id: str = "IL-GRACE-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def check_il_sb2637_scope(additive: str, is_food: bool = True) -> dict:
    """Check if an additive is covered by Illinois SB 2637 (BVO, Potassium Bromate, Propylparaben, Red 3)."""
    _req(additive, "additive")
    in_scope = bool(is_food) and str(additive).upper() in {"BVO", "POTASSIUM_BROMATE", "PROPYLPARABEN", "RED3"}
    return {"op": "check_il_sb2637_scope", "additive": str(additive).upper(), "in_scope": in_scope, "src": "recallstorm/states/il_food_safety_act.py"}


def evaluate_il_bakery_exemption(store_id: str, revenue_usd: float = 100000.0) -> dict:
    """Evaluate small-bakery exemption under Illinois food additive rules."""
    _req(store_id, "store_id")
    if revenue_usd < 0:
        raise DataValidationError("revenue_usd must be non-negative")
    return {"op": "evaluate_il_bakery_exemption", "store_id": str(store_id), "exempt": False, "src": "recallstorm/states/il_food_safety_act.py"}


def calculate_il_sell_through_days(days_remaining: int) -> int:
    """Return remaining sell-through days before Illinois enforcement."""
    if not isinstance(days_remaining, int):
        raise DataValidationError("days_remaining must be an int")
    return max(0, days_remaining)


def filter_il_jurisdiction_stores(stores: list[dict]) -> list[str]:
    """Filter store dicts to those located in Illinois ('IL')."""
    if stores is None:
        raise DataValidationError("stores cannot be None")
    return [str(s["store_id"]) for s in stores if str(s.get("state", "")).upper() == "IL"]


def parse_il_idph_guidance(guidance_text: str) -> dict:
    """Parse Illinois Department of Public Health (IDPH) additive guidance."""
    _req(guidance_text, "guidance_text")
    return {"op": "parse_il_idph_guidance", "effective_year": 2028, "length": len(str(guidance_text)), "src": "recallstorm/states/il_food_safety_act.py"}


def build_il_shelf_pull_order(store_id: str, sku_id: str, units: int = 10) -> dict:
    """Build an Illinois store shelf pull order."""
    _req(store_id, "store_id")
    _req(sku_id, "sku_id")
    if units < 0:
        raise DataValidationError("units must be non-negative")
    return {"op": "build_il_shelf_pull_order", "store_id": str(store_id), "sku_id": str(sku_id), "units": int(units), "src": "recallstorm/states/il_food_safety_act.py"}


def verify_il_reformulated_lot(lot_code: str, clean_prefix: str = "CLN") -> dict:
    """Verify whether a lot code reflects post-reformulation Illinois-compliant stock."""
    _req(lot_code, "lot_code")
    clean = str(lot_code).upper().startswith(str(clean_prefix).upper())
    return {"op": "verify_il_reformulated_lot", "lot_code": str(lot_code), "clean": clean, "src": "recallstorm/states/il_food_safety_act.py"}


def assess_il_distributor_liability(cases: int, fine_per_case: float = 250.0) -> float:
    """Assess potential distributor liability for non-compliant cases in Illinois."""
    if cases < 0 or fine_per_case < 0:
        raise DataValidationError("cases and fine_per_case must be non-negative")
    return round(float(cases) * float(fine_per_case), 2)


def format_il_inspection_sheet(store_id: str, checked_skus: int = 0) -> dict:
    """Format an IDPH store inspection readiness sheet."""
    _req(store_id, "store_id")
    return {"op": "format_il_inspection_sheet", "store_id": str(store_id), "checked_skus": int(checked_skus), "src": "recallstorm/states/il_food_safety_act.py"}


def track_il_phase_out_schedule(milestone: str, pct_complete: float = 100.0) -> dict:
    """Track vendor phase-out progress toward the Illinois SB 2637 deadline."""
    _req(milestone, "milestone")
    if not (0.0 <= pct_complete <= 100.0):
        raise DataValidationError("pct_complete must be in [0, 100]")
    return {"op": "track_il_phase_out_schedule", "milestone": str(milestone), "pct_complete": float(pct_complete), "src": "recallstorm/states/il_food_safety_act.py"}
