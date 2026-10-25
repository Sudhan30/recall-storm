"""Brominated vegetable oil (BVO) federal FDA revocation (21 CFR 180.30) and CA AB 418 rules."""
from __future__ import annotations

from datetime import datetime
from contract import DecidedBy, Rule, Sku, SkuDecision, Verdict
from recallstorm.aliases.detect import MatchResult, find_first_match
from recallstorm.core.ids import make_evidence_id


def bvo_aliases() -> tuple[str, ...]:
    """Return canonical aliases for brominated vegetable oil."""
    return ("brominated vegetable oil", "BVO", "E443", "aceite vegetal bromado", "huile vegetale bromee")


def bvo_effective(jurisdiction: str = "US") -> datetime:
    """Return effective datetime for BVO prohibition (FDA compliance date 2025-08-02, CA 2027-01-01)."""
    if jurisdiction.strip().upper() == "CA":
        return datetime(2027, 1, 1, 0, 0, 0)
    return datetime(2025, 8, 2, 0, 0, 0)


def bvo_rules() -> list[Rule]:
    """Return federal and California BVO rules."""
    return [
        Rule(
            rule_id="FDA_BVO_FOOD",
            additive="BVO",
            aliases=bvo_aliases(),
            jurisdictions=("US",),
            applies_to=("food",),
            effective=bvo_effective("US"),
            clause_ref="21 CFR 180.30 (revoked, 89 FR 55040)",
            source_text="FDA revoked the regulation authorizing the use of brominated vegetable oil (BVO) in food.",
        ),
        Rule(
            rule_id="CA_AB418_BVO",
            additive="BVO",
            aliases=bvo_aliases(),
            jurisdictions=("CA",),
            applies_to=("food",),
            effective=bvo_effective("CA"),
            clause_ref="Cal. Health & Safety Code 109025(a)(1)",
            source_text="Commencing January 1, 2027, brominated vegetable oil is prohibited in food in California.",
        ),
    ]


def detect_bvo(text: str) -> MatchResult | None:
    """Detect BVO in an ingredient statement."""
    return find_first_match(text, "BVO", bvo_aliases())


def bvo_beverage_scope(sku: Sku) -> bool:
    """Return True if SKU is a food/beverage item covered by BVO rules."""
    if not isinstance(sku, Sku):
        raise TypeError("sku must be a Sku")
    return bool(sku.is_food)


def bvo_rationale(match: MatchResult | None, rule_id: str = "FDA_BVO_FOOD") -> str:
    """Build a rationale string for BVO evaluation."""
    if match is None:
        return "No brominated vegetable oil (BVO) detected."
    return f"Contains prohibited BVO ('{match.match_text}' at [{match.start}:{match.end}]) under {rule_id}."


def evaluate_bvo_federal(sku: Sku, at: datetime) -> SkuDecision:
    """Evaluate a SKU against the federal FDA BVO rule."""
    if not isinstance(sku, Sku):
        raise TypeError("sku must be a Sku")
    wall = at.replace(tzinfo=None)
    if not bvo_beverage_scope(sku) or wall < bvo_effective("US"):
        return SkuDecision(sku.sku_id, Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, "Out of scope or before FDA BVO effective date.")
    m = detect_bvo(sku.ingredients)
    if m is not None:
        return SkuDecision(
            sku_id=sku.sku_id,
            verdict=Verdict.PULL,
            additive="BVO",
            match_text=m.match_text,
            match_start=m.start,
            match_end=m.end,
            rule_ids=("FDA_BVO_FOOD",),
            decided_by=DecidedBy.RULE,
            rationale=bvo_rationale(m, "FDA_BVO_FOOD"),
        )
    return SkuDecision(sku.sku_id, Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, bvo_rationale(None))


def bvo_evidence(sku: Sku, match: MatchResult, rule_id: str = "FDA_BVO_FOOD") -> dict:
    """Build an evidence dictionary for a BVO match."""
    return {
        "evidence_id": make_evidence_id(sku.sku_id, rule_id),
        "sku_id": sku.sku_id,
        "rule_id": rule_id,
        "clause_ref": "21 CFR 180.30 (revoked, 89 FR 55040)",
        "source_span": [match.start, match.end],
        "rationale": bvo_rationale(match, rule_id),
        "src": "recallstorm/rules/bvo.py",
    }


def bvo_summary(decisions: list[SkuDecision]) -> dict:
    """Summarize BVO decisions."""
    pulled = [d.sku_id for d in decisions if d.verdict == Verdict.PULL and d.additive == "BVO"]
    return {"additive": "BVO", "pulled_count": len(pulled), "pulled_skus": pulled}
