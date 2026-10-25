"""Immutable-style audit trail for SKU decisions and manual overrides."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from contract import SkuDecision
from recallstorm.adjudicate.overrides import Override


@dataclass
class AuditTrail:
    """Chronological log of automated decisions and human overrides."""

    entries: list[dict] = field(default_factory=list)


def record_decision(trail: AuditTrail, decision: SkuDecision, timestamp: datetime | str | None = None) -> dict:
    """Append a SkuDecision event to the audit trail."""
    if not isinstance(trail, AuditTrail) or not isinstance(decision, SkuDecision):
        raise TypeError("Expected AuditTrail and SkuDecision")
    ts = (
        timestamp.isoformat()
        if isinstance(timestamp, datetime)
        else (str(timestamp) if timestamp else datetime.now(tz=timezone.utc).isoformat())
    )
    entry = {
        "kind": "DECISION",
        "sku_id": decision.sku_id,
        "verdict": decision.verdict.value,
        "decided_by": decision.decided_by.value,
        "rule_ids": list(decision.rule_ids),
        "ts": ts,
    }
    trail.entries.append(entry)
    return entry


def record_override(trail: AuditTrail, override: Override, timestamp: datetime | str | None = None) -> dict:
    """Append an Override event to the audit trail."""
    if not isinstance(trail, AuditTrail) or not isinstance(override, Override):
        raise TypeError("Expected AuditTrail and Override")
    ts = (
        timestamp.isoformat()
        if isinstance(timestamp, datetime)
        else (str(timestamp) if timestamp else datetime.now(tz=timezone.utc).isoformat())
    )
    entry = {
        "kind": "OVERRIDE",
        "sku_id": override.sku_id,
        "verdict": override.new_verdict.value,
        "reviewer": override.reviewer,
        "reason_code": override.reason_code,
        "ts": ts,
    }
    trail.entries.append(entry)
    return entry


def audit_to_records(trail: AuditTrail) -> list[dict]:
    """Export all audit entries as a list of dictionaries."""
    return [dict(e) for e in trail.entries]


def decisions_by_source(trail: AuditTrail) -> dict[str, int]:
    """Count automated decisions by decided_by source (RULE vs MODEL)."""
    counts: dict[str, int] = {}
    for e in trail.entries:
        if e.get("kind") == "DECISION":
            src = str(e.get("decided_by", "RULE"))
            counts[src] = counts.get(src, 0) + 1
    return counts


def overrides_by_user(trail: AuditTrail) -> dict[str, int]:
    """Count manual overrides grouped by reviewer username."""
    counts: dict[str, int] = {}
    for e in trail.entries:
        if e.get("kind") == "OVERRIDE":
            user = str(e.get("reviewer", "unknown"))
            counts[user] = counts.get(user, 0) + 1
    return counts


def audit_summary(trail: AuditTrail) -> dict:
    """Return high-level summary metrics for an AuditTrail."""
    return {
        "total_entries": len(trail.entries),
        "by_source": decisions_by_source(trail),
        "by_user": overrides_by_user(trail),
    }


def audit_diff(t1: AuditTrail, t2: AuditTrail) -> dict:
    """Compare final verdicts per SKU between two AuditTrails."""
    v1 = {e["sku_id"]: e["verdict"] for e in t1.entries}
    v2 = {e["sku_id"]: e["verdict"] for e in t2.entries}
    changed = {k: (v1.get(k), v2.get(k)) for k in set(v1) | set(v2) if v1.get(k) != v2.get(k)}
    return {"changed_count": len(changed), "changes": changed}


def verify_audit(trail: AuditTrail) -> bool:
    """Verify that every entry in the AuditTrail has required keys and valid kind."""
    if not isinstance(trail, AuditTrail):
        return False
    for e in trail.entries:
        if e.get("kind") not in {"DECISION", "OVERRIDE"} or not e.get("sku_id") or not e.get("ts"):
            return False
    return True
