"""Interactive cashier register prompts for lot/date-code verification."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError
from recallstorm.gs1.lots import lot_matches_recall


@dataclass(frozen=True)
class CashierPromptConfig:
    """Configuration for POS cashier lot-check prompts."""

    ref_id: str = "PRM-CFG-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class LotCheckDialogBuilder:
    """Builder for interactive POS register lot verification dialogs."""

    ref_id: str = "PRM-DLG-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def configure_date_code_entry_prompt(sku_id: str, cutoff_date_iso: str) -> dict:
    """Configure a POS prompt requiring the cashier to key in the package Best-By date."""
    _req(sku_id, "sku_id")
    _req(cutoff_date_iso, "cutoff_date_iso")
    return {"op": "configure_date_code_entry_prompt", "sku_id": str(sku_id), "cutoff_date": str(cutoff_date_iso), "src": "recallstorm/pricing/register_prompts.py"}


def build_lot_prefix_validation_screen(sku_id: str, banned_prefixes: list[str]) -> dict:
    """Build a register screen blocking specific recalled lot prefixes while allowing clean lots."""
    _req(sku_id, "sku_id")
    if not banned_prefixes:
        raise DataValidationError("banned_prefixes cannot be empty")
    return {"op": "build_lot_prefix_validation_screen", "sku_id": str(sku_id), "banned_prefixes": sorted(banned_prefixes), "src": "recallstorm/pricing/register_prompts.py"}


def require_supervisor_key_flick_override(severity: str = "CLASS_I") -> bool:
    """Return True if a CSM supervisor key/badge is required to clear a register prompt."""
    _req(severity, "severity")
    return str(severity).upper() in {"CLASS_I", "CLASS I"}


def display_safe_lot_visual_guide(sku_id: str, diagram_url: str) -> dict:
    """Attach a package lot-stamp location diagram to the POS cashier touchscreen."""
    _req(sku_id, "sku_id")
    _req(diagram_url, "diagram_url")
    return {"op": "display_safe_lot_visual_guide", "sku_id": str(sku_id), "diagram_url": str(diagram_url), "src": "recallstorm/pricing/register_prompts.py"}


def capture_cashier_entered_lot_string(entered_lot: str, recalled_lots: list[str]) -> dict:
    """Evaluate a cashier-entered lot string against recalled_lots."""
    _req(entered_lot, "entered_lot")
    if recalled_lots is None:
        raise DataValidationError("recalled_lots cannot be None")
    blocked = lot_matches_recall(str(entered_lot), recalled_lots)
    return {"op": "capture_cashier_entered_lot_string", "entered_lot": str(entered_lot), "sale_blocked": blocked, "src": "recallstorm/pricing/register_prompts.py"}


def throttle_prompt_for_unaffected_upcs(upc: str, affected_upcs: set[str]) -> bool:
    """Return True if prompt should be shown (only for affected_upcs)."""
    _req(upc, "upc")
    if affected_upcs is None:
        raise DataValidationError("affected_upcs cannot be None")
    return str(upc).strip() in affected_upcs


def track_prompt_bypass_rate_by_cashier(bypasses: int, total_prompts: int) -> dict:
    """Flag cashiers who habitually bypass lot-check prompts (> 50% bypass rate)."""
    if bypasses < 0 or total_prompts <= 0 or bypasses > total_prompts:
        raise DataValidationError("Invalid bypass or prompt counts")
    rate = bypasses / total_prompts
    return {"op": "track_prompt_bypass_rate_by_cashier", "rate": round(rate, 4), "flagged": rate > 0.5, "src": "recallstorm/pricing/register_prompts.py"}


def localize_register_prompt_translations(prompt_en: str, lang: str = "es") -> dict:
    """Localize cashier prompt text."""
    _req(prompt_en, "prompt_en")
    return {"op": "localize_register_prompt_translations", "lang": str(lang), "text": f"[{lang.upper()}] {prompt_en}", "src": "recallstorm/pricing/register_prompts.py"}


def A_B_test_prompt_clarity_speed(secs_a: float, secs_b: float) -> str:
    """Select whichever prompt variant ('A' or 'B') has faster cashier verification time."""
    if secs_a <= 0 or secs_b <= 0:
        raise DataValidationError("Prompt durations must be positive")
    return "A" if secs_a <= secs_b else "B"


def disable_expired_lot_check_prompts(sku_id: str, days_since_recall: int, max_days: int = 90) -> dict:
    """Retire lot-check prompts once all affected shelf life has passed."""
    _req(sku_id, "sku_id")
    if days_since_recall < 0 or max_days <= 0:
        raise DataValidationError("Invalid days")
    return {"op": "disable_expired_lot_check_prompts", "sku_id": str(sku_id), "disabled": days_since_recall >= max_days, "src": "recallstorm/pricing/register_prompts.py"}
