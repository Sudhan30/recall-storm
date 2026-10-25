"""Compliance officer overrides for SKU decisions."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from contract import DecidedBy, SkuDecision, Verdict
from recallstorm.core.errors import DataValidationError

_REASON_CODES: tuple[str, ...] = (
    "VENDOR_COA_VERIFIED",
    "REFORMULATED_BATCH",
    "LAB_TEST_NEGATIVE",
    "CONFIRMED_POSITIVE_BY_LAB",
    "MANUAL_LABEL_INSPECTION",
)


@dataclass(frozen=True)
class Override:
    """Manual override applied to a SKU verdict."""

    sku_id: str
    new_verdict: Verdict
    reason_code: str
    reviewer: str
    notes: str = ""
    expires_at: datetime | None = None


@dataclass
class OverrideBook:
    """Collection of active overrides indexed by sku_id."""

    overrides: list[Override] = field(default_factory=list)


def override_reason_codes() -> tuple[str, ...]:
    """Return valid reason codes for manual overrides."""
    return _REASON_CODES


def validate_override(override: Override) -> list[str]:
    """Validate an Override object."""
    if not isinstance(override, Override):
        return ["Not an Override instance"]
    issues: list[str] = []
    if not override.sku_id.strip():
        issues.append("sku_id is empty")
    if not isinstance(override.new_verdict, Verdict):
        issues.append("new_verdict must be a Verdict enum")
    if override.reason_code not in _REASON_CODES:
        issues.append(f"invalid reason_code: {override.reason_code}")
    if not override.reviewer.strip():
        issues.append("reviewer is empty")
    return issues


def apply_override(decision: SkuDecision, override: Override) -> SkuDecision:
    """Apply a validated Override to an existing SkuDecision."""
    if not isinstance(decision, SkuDecision):
        raise TypeError("decision must be a SkuDecision")
    issues = validate_override(override)
    if issues:
        raise DataValidationError("; ".join(issues))
    if decision.sku_id != override.sku_id:
        raise DataValidationError(f"Override sku_id {override.sku_id} does not match {decision.sku_id}")
    return SkuDecision(
        sku_id=decision.sku_id,
        verdict=override.new_verdict,
        additive=decision.additive if override.new_verdict != Verdict.KEEP else None,
        match_text=decision.match_text if override.new_verdict != Verdict.KEEP else None,
        match_start=decision.match_start if override.new_verdict != Verdict.KEEP else None,
        match_end=decision.match_end if override.new_verdict != Verdict.KEEP else None,
        rule_ids=decision.rule_ids if override.new_verdict != Verdict.KEEP else (),
        decided_by=DecidedBy.RULE,
        rationale=f"Override ({override.reason_code}) by {override.reviewer}: {override.notes or decision.rationale}",
    )


def override_to_record(override: Override) -> dict:
    """Serialize an Override to a dictionary."""
    return {
        "sku_id": override.sku_id,
        "new_verdict": override.new_verdict.value,
        "reason_code": override.reason_code,
        "reviewer": override.reviewer,
        "notes": override.notes,
        "expires_at": override.expires_at.isoformat() if override.expires_at else None,
    }


def overrides_for_sku(overrides: list[Override], sku_id: str) -> list[Override]:
    """Return all overrides matching sku_id."""
    return [o for o in overrides if o.sku_id == sku_id]


def expire_overrides(overrides: list[Override], now: datetime) -> list[Override]:
    """Filter out overrides whose expires_at is <= now."""
    return [o for o in overrides if o.expires_at is None or o.expires_at > now]


def override_report(overrides: list[Override]) -> dict:
    """Summarize overrides by verdict and reason code."""
    by_code: dict[str, int] = {}
    for o in overrides:
        by_code[o.reason_code] = by_code.get(o.reason_code, 0) + 1
    return {"total": len(overrides), "by_reason": by_code}
