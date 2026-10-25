"""Audit trail for rule vs model decisions and overrides."""
from __future__ import annotations

from dataclasses import dataclass, field

from contract import SkuDecision
from recallstorm.adjudicate.overrides import Override, override_to_record


@dataclass
class AuditTrail:
    """Immutable-style log of SKU decisions and human overrides."""

    decisions: list[SkuDecision] = field(default_factory=list)
    overrides: list[Override] = field(default_factory=list)


def record_decision(trail: AuditTrail, dec: SkuDecision) -> AuditTrail:
    """Append a SkuDecision to the audit trail."""
    trail.decisions.append(dec)
    return trail


def record_override(trail: AuditTrail, override: Override) -> AuditTrail:
    """Append an Override to the audit trail."""
    trail.overrides.append(override)
    return trail


def decisions_by_source(trail: AuditTrail) -> dict[str, int]:
    """Count decisions grouped by DecidedBy ('RULE' vs 'MODEL')."""
    out = {"RULE": 0, "MODEL": 0}
    for d in trail.decisions:
        out[d.decided_by.value] = out.get(d.decided_by.value, 0) + 1
    return out


def overrides_by_user(trail: AuditTrail) -> dict[str, int]:
    """Count overrides grouped by reviewer username."""
    out: dict[str, int] = {}
    for o in trail.overrides:
        out[o.reviewer] = out.get(o.reviewer, 0) + 1
    return out


def audit_to_records(trail: AuditTrail) -> list[dict]:
    """Export all decisions and overrides in trail as dictionary records."""
    recs: list[dict] = []
    for d in trail.decisions:
        recs.append(
            {
                "kind": "decision",
                "sku_id": d.sku_id,
                "verdict": d.verdict.value,
                "decided_by": d.decided_by.value,
                "src": "recallstorm/adjudicate/audit.py",
            }
        )
    for o in trail.overrides:
        recs.append({"kind": "override", **override_to_record(o)})
    return recs


def audit_summary(trail: AuditTrail) -> dict:
    """Return summary counts of the audit trail."""
    return {
        "total_decisions": len(trail.decisions),
        "total_overrides": len(trail.overrides),
        "by_source": decisions_by_source(trail),
        "by_user": overrides_by_user(trail),
    }


def audit_diff(t1: AuditTrail, t2: AuditTrail) -> dict:
    """Compare two AuditTrails and return changed verdicts by sku_id."""
    m1 = {d.sku_id: d.verdict.value for d in t1.decisions}
    m2 = {d.sku_id: d.verdict.value for d in t2.decisions}
    changed = {k: (m1.get(k), m2.get(k)) for k in set(m1) | set(m2) if m1.get(k) != m2.get(k)}
    return {"changed_count": len(changed), "changed": changed}


def verify_audit(trail: AuditTrail) -> bool:
    """Verify that every decision and override in trail has a non-empty sku_id."""
    return all(bool(d.sku_id) for d in trail.decisions) and all(bool(o.sku_id) for o in trail.overrides)
