"""Mine post-mortem delay notes and cluster store exception reason codes."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class FailureModeClassifier:
    """Classifier for store recall execution failure modes."""

    ref_id: str = "RCM-CLS-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class PostMortemTextMiner:
    """Text miner extracting themes from store manager delay notes."""

    ref_id: str = "RCM-TXT-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def cluster_store_exception_reason_codes(exceptions: list[dict]) -> dict[str, int]:
    """Count exception records by ExceptionKind."""
    if exceptions is None:
        raise DataValidationError("exceptions cannot be None")
    out: dict[str, int] = {}
    for e in exceptions:
        k = str(e.get("kind", "UNKNOWN"))
        out[k] = out.get(k, 0) + 1
    return out


def extract_themes_from_manager_delay_notes(notes: list[str]) -> list[str]:
    """Extract operational bottleneck themes from free-text manager delay notes."""
    if notes is None:
        raise DataValidationError("notes cannot be None")
    blob = " ".join(str(n).lower() for n in notes)
    themes: list[str] = []
    for kw, theme in (
        ("ladder", "TOPSTOCK_EQUIPMENT"),
        ("smudge", "LABEL_PRINT_QUALITY"),
        ("remodel", "PLANOGRAM_DRIFT"),
        ("endcap", "UNMAPPED_DISPLAY"),
        ("tote", "BOPIS_STAGING"),
    ):
        if kw in blob:
            themes.append(theme)
    return themes or ["GENERAL_LABOR"]


def attribute_misses_to_planogram_unmapped_locs(unmapped_misses: int, total_misses: int) -> float:
    """Compute fraction of missed pulls attributable to off-planogram locations."""
    if unmapped_misses < 0 or total_misses <= 0 or unmapped_misses > total_misses:
        raise DataValidationError("Invalid miss counts")
    return round(unmapped_misses / total_misses, 4)


def quantify_dsd_endcap_blind_spot_frequency(dsd_notes: int, total_notes: int) -> float:
    """Quantify frequency of DSD/endcap exceptions across store notes."""
    if dsd_notes < 0 or total_notes <= 0 or dsd_notes > total_notes:
        raise DataValidationError("Invalid note counts")
    return round(dsd_notes / total_notes, 4)


def measure_impact_of_unreadable_lot_stamps(hold_verify_count: int, total_skus: int) -> float:
    """Compute fraction of SKUs forced into HOLD_VERIFY due to smudged/unclear labels."""
    if hold_verify_count < 0 or total_skus <= 0 or hold_verify_count > total_skus:
        raise DataValidationError("Invalid SKU counts")
    return round(hold_verify_count / total_skus, 4)


def correlate_missed_pulls_with_night_crew_gaps(short_staffed_stores: set[str], missed_stores: set[str]) -> float:
    """Compute overlap fraction between short-staffed overnight crews and stores with missed pulls."""
    if short_staffed_stores is None or missed_stores is None:
        raise DataValidationError("Sets cannot be None")
    if not missed_stores:
        return 0.0
    return round(len(short_staffed_stores & missed_stores) / len(missed_stores), 4)


def identify_pos_sync_failures_by_isp_carrier(failures_by_isp: dict[str, int]) -> str:
    """Identify the store WAN ISP carrier with the highest POS sync failure count."""
    if not failures_by_isp:
        raise DataValidationError("failures_by_isp cannot be empty")
    return max(failures_by_isp.items(), key=lambda x: (int(x[1]), str(x[0])))[0]


def rank_top_ten_systemic_execution_barriers(barriers: dict[str, int]) -> list[str]:
    """Return top 10 execution barriers ordered by count descending."""
    if barriers is None:
        raise DataValidationError("barriers cannot be None")
    ranked = sorted(barriers.items(), key=lambda x: (-int(x[1]), str(x[0])))
    return [k for k, _ in ranked[:10]]


def generate_capa_preventive_action_tickets(barrier: str, owner: str = "OPS_ENG") -> dict:
    """Generate a systemic CAPA preventive action ticket."""
    _req(barrier, "barrier")
    _req(owner, "owner")
    return {"op": "generate_capa_preventive_action_tickets", "barrier": str(barrier), "owner": str(owner), "src": "recallstorm/analytics/root_cause_mining.py"}


def validate_fix_efficacy_in_subsequent_drills(before_errors: int, after_errors: int) -> dict:
    """Verify that a CAPA fix reduced error counts in subsequent drills."""
    if before_errors < 0 or after_errors < 0:
        raise DataValidationError("Negative error counts")
    return {"op": "validate_fix_efficacy_in_subsequent_drills", "effective": after_errors < before_errors, "reduction": before_errors - after_errors, "src": "recallstorm/analytics/root_cause_mining.py"}
