"""Human adjudication overrides for SKU decisions."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from contract import DecidedBy, SkuDecision, Verdict

_REASON_CODES: tuple[str, ...] = (
    "LAB_COA_VERIFIED",
    "REFORMULATED_CLEAN_LOT",
    "VENDOR_ATTESTATION",
    "OCR_MISREAD_CORRECTED",
    "MANUAL_PULL_CONFIRMATION",
)


@dataclass(frozen=True)
class Override:
    """Manual reviewer override for a SKU verdict."""

    sku_id: str
    verdict: Verdict
    reason_code: str
    reviewer: str
    notes: str = ""
    expires_at: datetime | None = None


@dataclass
class OverrideBook:
    """Collection of active reviewer Overrides."""

    overrides: list[Override] = field(default_factory=list)


def override_reason_codes() -> tuple[str, ...]:
    """Return allowed override reason codes."""
    return _REASON_CODES


def validate_override(override: Override) -> list[str]:
    """Validate an Override instance."""
    issues: list[str] = []
    if not override.sku_id.strip():
        issues.append("sku_id is empty")
    if not isinstance(override.verdict, Verdict):
        issues.append("invalid verdict")
    if override.reason_code not in _REASON_CODES:
        issues.append(f"invalid reason_code: {override.reason_code!r}")
    if not override.reviewer.strip():
        issues.append("reviewer is empty")
    return issues


def apply_override(decision: SkuDecision, override: Override) -> SkuDecision:
    """Apply a validated Override to a SkuDecision."""
    if decision.sku_id != override.sku_id:
        raise ValueError(f"Override sku_id {override.sku_id} does not match decision {decision.sku_id}")
    return SkuDecision(
        sku_id=decision.sku_id,
        verdict=override.verdict,
        additive=decision.additive,
        match_text=decision.match_text,
        match_start=decision.match_start,
        match_end=decision.match_end,
        rule_ids=decision.rule_ids,
        decided_by=DecidedBy.RULE,
        rationale=f"Override ({override.reason_code}) by {override.reviewer}: {override.notes or decision.rationale}",
    )


def override_to_record(override: Override) -> dict:
    """Serialize an Override to a dictionary record."""
    return {
        "sku_id": override.sku_id,
        "verdict": override.verdict.value,
        "reason_code": override.reason_code,
        "reviewer": override.reviewer,
        "notes": override.notes,
        "expires_at": override.expires_at.isoformat() if override.expires_at else None,
        "src": "recallstorm/adjudicate/overrides.py",
    }


def overrides_for_sku(overrides: list[Override], sku_id: str) -> list[Override]:
    """Return all overrides matching sku_id."""
    return [o for o in overrides if o.sku_id == sku_id]


def expire_overrides(overrides: list[Override], now: datetime) -> list[Override]:
    """Filter out overrides whose expires_at is at or before now."""
    return [o for o in overrides if o.expires_at is None or o.expires_at > now]


def override_report(overrides: list[Override]) -> dict:
    """Summarize overrides by verdict and reason_code."""
    by_reason: dict[str, int] = {}
    for o in overrides:
        by_reason[o.reason_code] = by_reason.get(o.reason_code, 0) + 1
    return {"total": len(overrides), "by_reason": by_reason}
