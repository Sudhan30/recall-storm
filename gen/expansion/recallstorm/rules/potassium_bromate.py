"""Potassium bromate rule evaluation under CA AB 418."""
from __future__ import annotations

from datetime import datetime
from contract import DecidedBy, Rule, Sku, SkuDecision, Verdict
from recallstorm.aliases.detect import MatchResult, find_first_match
from recallstorm.core.ids import make_evidence_id


def bromate_aliases() -> tuple[str, ...]:
    """Return canonical aliases for potassium bromate."""
    return ("potassium bromate", "bromated flour", "bromated wheat flour", "E924", "E924a", "bromato de potasio")


def bromate_effective() -> datetime:
    """Return naive local effective datetime for CA AB 418 potassium bromate ban."""
    return datetime(2027, 1, 1, 0, 0, 0)


def bromate_rules() -> list[Rule]:
    """Return Rule definitions for potassium bromate."""
    return [
        Rule(
            rule_id="CA_AB418_BROMATE",
            additive="POTASSIUM_BROMATE",
            aliases=bromate_aliases(),
            jurisdictions=("CA",),
            applies_to=("food",),
            effective=bromate_effective(),
            clause_ref="Cal. Health & Safety Code 109025(a)(2)",
            source_text="Commencing January 1, 2027, potassium bromate is prohibited in food in California.",
        )
    ]


def detect_bromate(text: str) -> MatchResult | None:
    """Detect potassium bromate in an ingredient statement."""
    return find_first_match(text, "POTASSIUM_BROMATE", bromate_aliases())


def bromate_scope(sku: Sku) -> bool:
    """Return True if SKU is in scope for potassium bromate rules (food items)."""
    if not isinstance(sku, Sku):
        raise TypeError("sku must be a Sku")
    return bool(sku.is_food)


def bromate_rationale(match: MatchResult | None) -> str:
    """Generate a rationale string for potassium bromate evaluation."""
    if match is None:
        return "No potassium bromate detected."
    return f"Contains prohibited potassium bromate ('{match.match_text}' at [{match.start}:{match.end}]) under Cal. HSC 109025(a)(2)."


def evaluate_bromate(sku: Sku, at: datetime) -> SkuDecision:
    """Evaluate a SKU for potassium bromate at the given datetime."""
    if not isinstance(sku, Sku):
        raise TypeError("sku must be a Sku")
    if not isinstance(at, datetime):
        raise TypeError("at must be a datetime")
    wall = at.replace(tzinfo=None)
    if not bromate_scope(sku) or wall < bromate_effective():
        return SkuDecision(sku.sku_id, Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, "Out of scope or before effective date.")
    m = detect_bromate(sku.ingredients)
    if m is not None:
        return SkuDecision(
            sku_id=sku.sku_id,
            verdict=Verdict.PULL,
            additive="POTASSIUM_BROMATE",
            match_text=m.match_text,
            match_start=m.start,
            match_end=m.end,
            rule_ids=("CA_AB418_BROMATE",),
            decided_by=DecidedBy.RULE,
            rationale=bromate_rationale(m),
        )
    return SkuDecision(sku.sku_id, Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, bromate_rationale(None))


def bromate_evidence(sku: Sku, match: MatchResult) -> dict:
    """Build an evidence record dictionary for a potassium bromate match."""
    return {
        "evidence_id": make_evidence_id(sku.sku_id, "CA_AB418_BROMATE"),
        "sku_id": sku.sku_id,
        "rule_id": "CA_AB418_BROMATE",
        "clause_ref": "Cal. Health & Safety Code 109025(a)(2)",
        "source_span": [match.start, match.end],
        "rationale": bromate_rationale(match),
        "src": "recallstorm/rules/potassium_bromate.py",
    }


def bromate_summary(decisions: list[SkuDecision]) -> dict:
    """Summarize potassium bromate decisions."""
    pulled = [d.sku_id for d in decisions if d.verdict == Verdict.PULL and d.additive == "POTASSIUM_BROMATE"]
    return {"additive": "POTASSIUM_BROMATE", "pulled_count": len(pulled), "pulled_skus": pulled}
