"""Propylparaben rule evaluation under CA AB 418."""
from __future__ import annotations

from datetime import datetime
from contract import DecidedBy, Rule, Sku, SkuDecision, Verdict
from recallstorm.aliases.detect import MatchResult, find_first_match
from recallstorm.core.ids import make_evidence_id


def paraben_aliases() -> tuple[str, ...]:
    """Return canonical aliases for propylparaben."""
    return ("propylparaben", "propyl paraben", "propyl p-hydroxybenzoate", "E216", "E217", "propilparabeno")


def paraben_effective() -> datetime:
    """Return naive local effective datetime for CA AB 418 propylparaben ban."""
    return datetime(2027, 1, 1, 0, 0, 0)


def paraben_rules() -> list[Rule]:
    """Return Rule definitions for propylparaben."""
    return [
        Rule(
            rule_id="CA_AB418_PROPYLPARABEN",
            additive="PROPYLPARABEN",
            aliases=paraben_aliases(),
            jurisdictions=("CA",),
            applies_to=("food",),
            effective=paraben_effective(),
            clause_ref="Cal. Health & Safety Code 109025(a)(3)",
            source_text="Commencing January 1, 2027, propylparaben is prohibited in food in California.",
        )
    ]


def detect_propylparaben(text: str) -> MatchResult | None:
    """Detect propylparaben in an ingredient statement."""
    return find_first_match(text, "PROPYLPARABEN", paraben_aliases())


def paraben_scope(sku: Sku) -> bool:
    """Return True if SKU is in food scope for propylparaben."""
    if not isinstance(sku, Sku):
        raise TypeError("sku must be a Sku")
    return bool(sku.is_food)


def paraben_rationale(match: MatchResult | None) -> str:
    """Generate a rationale string for propylparaben evaluation."""
    if match is None:
        return "No propylparaben detected."
    return f"Contains prohibited propylparaben ('{match.match_text}' at [{match.start}:{match.end}]) under Cal. HSC 109025(a)(3)."


def evaluate_propylparaben(sku: Sku, at: datetime) -> SkuDecision:
    """Evaluate a SKU for propylparaben at the given datetime."""
    if not isinstance(sku, Sku):
        raise TypeError("sku must be a Sku")
    if not isinstance(at, datetime):
        raise TypeError("at must be a datetime")
    wall = at.replace(tzinfo=None)
    if not paraben_scope(sku) or wall < paraben_effective():
        return SkuDecision(sku.sku_id, Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, "Out of scope or before effective date.")
    m = detect_propylparaben(sku.ingredients)
    if m is not None:
        return SkuDecision(
            sku_id=sku.sku_id,
            verdict=Verdict.PULL,
            additive="PROPYLPARABEN",
            match_text=m.match_text,
            match_start=m.start,
            match_end=m.end,
            rule_ids=("CA_AB418_PROPYLPARABEN",),
            decided_by=DecidedBy.RULE,
            rationale=paraben_rationale(m),
        )
    return SkuDecision(sku.sku_id, Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, paraben_rationale(None))


def paraben_evidence(sku: Sku, match: MatchResult) -> dict:
    """Build an evidence record dictionary for a propylparaben match."""
    return {
        "evidence_id": make_evidence_id(sku.sku_id, "CA_AB418_PROPYLPARABEN"),
        "sku_id": sku.sku_id,
        "rule_id": "CA_AB418_PROPYLPARABEN",
        "clause_ref": "Cal. Health & Safety Code 109025(a)(3)",
        "source_span": [match.start, match.end],
        "rationale": paraben_rationale(match),
        "src": "recallstorm/rules/propylparaben.py",
    }


def paraben_summary(decisions: list[SkuDecision]) -> dict:
    """Summarize propylparaben decisions."""
    pulled = [d.sku_id for d in decisions if d.verdict == Verdict.PULL and d.additive == "PROPYLPARABEN"]
    return {"additive": "PROPYLPARABEN", "pulled_count": len(pulled), "pulled_skus": pulled}
