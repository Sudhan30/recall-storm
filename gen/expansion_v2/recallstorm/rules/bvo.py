"""Brominated Vegetable Oil (BVO) federal FDA revocation and state rules."""
from __future__ import annotations

from datetime import datetime

from contract import DecidedBy, Rule, Sku, SkuDecision, Verdict
from recallstorm.aliases.detect import MatchResult, find_first_match
from recallstorm.core.ids import make_evidence_id


def bvo_aliases() -> tuple[str, ...]:
    """Return canonical aliases for Brominated Vegetable Oil."""
    return ("brominated vegetable oil", "BVO", "E443", "aceite vegetal bromado")


def bvo_effective() -> datetime:
    """Return the federal FDA BVO compliance deadline (2025-08-02T00:00:00)."""
    return datetime(2025, 8, 2, 0, 0, 0)


def bvo_rules() -> list[Rule]:
    """Return federal FDA and CA AB 418 BVO rules."""
    return [
        Rule(
            rule_id="FDA_BVO_FOOD",
            additive="BVO",
            aliases=bvo_aliases(),
            jurisdictions=("US",),
            applies_to=("food",),
            effective=bvo_effective(),
            clause_ref="21 CFR 180.30 (revoked, 89 FR 55040)",
            source_text="FDA revoked the regulation authorizing the use of brominated vegetable oil (BVO) in food.",
        ),
        Rule(
            rule_id="CA_AB418_BVO",
            additive="BVO",
            aliases=bvo_aliases(),
            jurisdictions=("CA",),
            applies_to=("food",),
            effective=datetime(2027, 1, 1, 0, 0, 0),
            clause_ref="Cal. Health & Safety Code 109025(a)(1)",
            source_text="Prohibits food products containing brominated vegetable oil commencing January 1, 2027.",
        ),
    ]


def bvo_beverage_scope(sku: Sku) -> bool:
    """Return True if sku is a food/beverage product in scope for BVO revocation."""
    return bool(sku.is_food)


def detect_bvo(text: str) -> MatchResult | None:
    """Detect Brominated Vegetable Oil in an ingredient string."""
    return find_first_match(text, bvo_aliases(), additive="BVO")


def bvo_rationale(sku: Sku, match: MatchResult | None) -> str:
    """Build rationale string for BVO evaluation."""
    if match:
        return f"SKU {sku.sku_id} contains Brominated Vegetable Oil ({match.match_text!r}) revoked under 21 CFR 180.30."
    return f"SKU {sku.sku_id} does not contain Brominated Vegetable Oil."


def bvo_evidence(sku: Sku, match: MatchResult) -> dict:
    """Build an evidence record for a BVO match."""
    return {
        "type": "evidence",
        "evidence_id": make_evidence_id(sku.sku_id, "FDA_BVO_FOOD"),
        "sku_id": sku.sku_id,
        "rule_id": "FDA_BVO_FOOD",
        "clause_ref": "21 CFR 180.30 (revoked, 89 FR 55040)",
        "source_span": {"start": match.start, "end": match.end, "text": match.match_text},
        "rationale": bvo_rationale(sku, match),
        "src": "recallstorm/rules/bvo.py",
    }


def evaluate_bvo_federal(sku: Sku, state: str, at: datetime) -> SkuDecision:
    """Evaluate a Sku against the federal FDA BVO revocation rule."""
    wall = at.replace(tzinfo=None)
    if not bvo_beverage_scope(sku) or wall < bvo_effective():
        return SkuDecision(sku.sku_id, Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, "Out of scope or pre-effective")
    m = detect_bvo(sku.ingredients)
    if m:
        rids = ("FDA_BVO_FOOD", "CA_AB418_BVO") if (state.upper() == "CA" and wall >= datetime(2027, 1, 1)) else ("FDA_BVO_FOOD",)
        return SkuDecision(
            sku_id=sku.sku_id,
            verdict=Verdict.PULL,
            additive="BVO",
            match_text=m.match_text,
            match_start=m.start,
            match_end=m.end,
            rule_ids=rids,
            decided_by=DecidedBy.RULE,
            rationale=bvo_rationale(sku, m),
        )
    return SkuDecision(sku.sku_id, Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, bvo_rationale(sku, None))


def bvo_summary(decisions: list[SkuDecision]) -> dict:
    """Summarize BVO decisions."""
    pulled = [d.sku_id for d in decisions if d.verdict == Verdict.PULL and d.additive == "BVO"]
    return {"total": len(decisions), "pulled_count": len(pulled), "pulled_skus": pulled}
