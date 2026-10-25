"""Potassium bromate rule evaluation (CA AB 418)."""
from __future__ import annotations

from datetime import datetime

from contract import DecidedBy, Rule, Sku, SkuDecision, Verdict
from recallstorm.aliases.detect import MatchResult, find_first_match
from recallstorm.core.ids import make_evidence_id


def bromate_aliases() -> tuple[str, ...]:
    """Return canonical aliases for potassium bromate."""
    return ("potassium bromate", "bromated flour", "E924", "E924a", "bromato de potasio")


def bromate_effective() -> datetime:
    """Return the naive local effective date for CA AB 418 potassium bromate prohibition."""
    return datetime(2027, 1, 1, 0, 0, 0)


def bromate_rules() -> list[Rule]:
    """Return the CA AB 418 Rule for potassium bromate."""
    return [
        Rule(
            rule_id="CA_AB418_BROMATE",
            additive="POTASSIUM_BROMATE",
            aliases=bromate_aliases(),
            jurisdictions=("CA",),
            applies_to=("food",),
            effective=bromate_effective(),
            clause_ref="Cal. Health & Safety Code 109025(a)(2)",
            source_text="Prohibits food products containing potassium bromate commencing January 1, 2027.",
        )
    ]


def bromate_scope(sku: Sku) -> bool:
    """Return True if sku is a food product subject to potassium bromate rules."""
    return bool(sku.is_food)


def detect_bromate(text: str) -> MatchResult | None:
    """Detect potassium bromate in an ingredient string."""
    return find_first_match(text, bromate_aliases(), additive="POTASSIUM_BROMATE")


def bromate_rationale(sku: Sku, match: MatchResult | None) -> str:
    """Build rationale string for potassium bromate decision."""
    if match:
        return f"SKU {sku.sku_id} contains potassium bromate ({match.match_text!r}) prohibited under CA AB 418."
    return f"SKU {sku.sku_id} does not contain potassium bromate."


def bromate_evidence(sku: Sku, match: MatchResult) -> dict:
    """Build an evidence record for a potassium bromate match."""
    return {
        "type": "evidence",
        "evidence_id": make_evidence_id(sku.sku_id, "CA_AB418_BROMATE"),
        "sku_id": sku.sku_id,
        "rule_id": "CA_AB418_BROMATE",
        "clause_ref": "Cal. Health & Safety Code 109025(a)(2)",
        "source_span": {"start": match.start, "end": match.end, "text": match.match_text},
        "rationale": bromate_rationale(sku, match),
        "src": "recallstorm/rules/potassium_bromate.py",
    }


def evaluate_bromate(sku: Sku, state: str, at: datetime) -> SkuDecision:
    """Evaluate a Sku against the CA AB 418 potassium bromate rule."""
    wall = at.replace(tzinfo=None)
    if state.upper() != "CA" or not bromate_scope(sku) or wall < bromate_effective():
        return SkuDecision(sku.sku_id, Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, "Out of scope or pre-effective")
    m = detect_bromate(sku.ingredients)
    if m:
        return SkuDecision(
            sku_id=sku.sku_id,
            verdict=Verdict.PULL,
            additive="POTASSIUM_BROMATE",
            match_text=m.match_text,
            match_start=m.start,
            match_end=m.end,
            rule_ids=("CA_AB418_BROMATE",),
            decided_by=DecidedBy.RULE,
            rationale=bromate_rationale(sku, m),
        )
    return SkuDecision(sku.sku_id, Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, bromate_rationale(sku, None))


def bromate_summary(decisions: list[SkuDecision]) -> dict:
    """Summarize potassium bromate decisions."""
    pulled = [d.sku_id for d in decisions if d.verdict == Verdict.PULL and d.additive == "POTASSIUM_BROMATE"]
    return {"total": len(decisions), "pulled_count": len(pulled), "pulled_skus": pulled}
