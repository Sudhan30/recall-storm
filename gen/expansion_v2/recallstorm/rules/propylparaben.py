"""Propylparaben rule evaluation (CA AB 418)."""
from __future__ import annotations

from datetime import datetime

from contract import DecidedBy, Rule, Sku, SkuDecision, Verdict
from recallstorm.aliases.detect import MatchResult, find_first_match
from recallstorm.core.ids import make_evidence_id


def paraben_aliases() -> tuple[str, ...]:
    """Return canonical aliases for propylparaben."""
    return (
        "propylparaben",
        "propyl paraben",
        "propyl p-hydroxybenzoate",
        "propyl 4-hydroxybenzoate",
        "E216",
        "E217",
        "propilparabeno",
    )


def paraben_effective() -> datetime:
    """Return naive local effective date for CA AB 418 propylparaben prohibition."""
    return datetime(2027, 1, 1, 0, 0, 0)


def paraben_rules() -> list[Rule]:
    """Return CA AB 418 Rule for propylparaben."""
    return [
        Rule(
            rule_id="CA_AB418_PROPYLPARABEN",
            additive="PROPYLPARABEN",
            aliases=paraben_aliases(),
            jurisdictions=("CA",),
            applies_to=("food",),
            effective=paraben_effective(),
            clause_ref="Cal. Health & Safety Code 109025(a)(3)",
            source_text="Prohibits food products containing propylparaben commencing January 1, 2027.",
        )
    ]


def paraben_scope(sku: Sku) -> bool:
    """Return True if sku is a food product in scope for propylparaben rules."""
    return bool(sku.is_food)


def detect_propylparaben(text: str) -> MatchResult | None:
    """Detect propylparaben in an ingredient string."""
    return find_first_match(text, paraben_aliases(), additive="PROPYLPARABEN")


def paraben_rationale(sku: Sku, match: MatchResult | None) -> str:
    """Build rationale string for propylparaben decision."""
    if match:
        return f"SKU {sku.sku_id} contains propylparaben ({match.match_text!r}) prohibited under CA AB 418."
    return f"SKU {sku.sku_id} does not contain propylparaben."


def paraben_evidence(sku: Sku, match: MatchResult) -> dict:
    """Build an evidence record for a propylparaben match."""
    return {
        "type": "evidence",
        "evidence_id": make_evidence_id(sku.sku_id, "CA_AB418_PROPYLPARABEN"),
        "sku_id": sku.sku_id,
        "rule_id": "CA_AB418_PROPYLPARABEN",
        "clause_ref": "Cal. Health & Safety Code 109025(a)(3)",
        "source_span": {"start": match.start, "end": match.end, "text": match.match_text},
        "rationale": paraben_rationale(sku, match),
        "src": "recallstorm/rules/propylparaben.py",
    }


def evaluate_propylparaben(sku: Sku, state: str, at: datetime) -> SkuDecision:
    """Evaluate a Sku against the CA AB 418 propylparaben rule."""
    wall = at.replace(tzinfo=None)
    if state.upper() != "CA" or not paraben_scope(sku) or wall < paraben_effective():
        return SkuDecision(sku.sku_id, Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, "Out of scope or pre-effective")
    m = detect_propylparaben(sku.ingredients)
    if m:
        return SkuDecision(
            sku_id=sku.sku_id,
            verdict=Verdict.PULL,
            additive="PROPYLPARABEN",
            match_text=m.match_text,
            match_start=m.start,
            match_end=m.end,
            rule_ids=("CA_AB418_PROPYLPARABEN",),
            decided_by=DecidedBy.RULE,
            rationale=paraben_rationale(sku, m),
        )
    return SkuDecision(sku.sku_id, Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, paraben_rationale(sku, None))


def paraben_summary(decisions: list[SkuDecision]) -> dict:
    """Summarize propylparaben decisions."""
    pulled = [d.sku_id for d in decisions if d.verdict == Verdict.PULL and d.additive == "PROPYLPARABEN"]
    return {"total": len(decisions), "pulled_count": len(pulled), "pulled_skus": pulled}
