"""Minnesota Amara's Law (Minn. Stat. 116.943) prohibiting intentionally added PFAS in 11 product categories."""
from __future__ import annotations

from datetime import datetime
from contract import DecidedBy, Rule, Sku, SkuDecision, Verdict
from recallstorm.aliases.detect import MatchResult, find_first_match
from recallstorm.core.ids import make_evidence_id

_PFAS_CATEGORIES: tuple[str, ...] = (
    "carpets",
    "cleaning products",
    "cookware",
    "cosmetics",
    "dental floss",
    "fabric treatments",
    "juvenile products",
    "menstruation products",
    "textile furnishings",
    "ski wax",
    "upholstered furniture",
)


def pfas_product_categories() -> tuple[str, ...]:
    """Return the 11 product categories covered by Minn. Stat. 116.943 Subd. 5 (2025)."""
    return _PFAS_CATEGORIES


def pfas_effective() -> datetime:
    """Return effective datetime of Minnesota PFAS ban for the 11 categories (2025-01-01)."""
    return datetime(2025, 1, 1, 0, 0, 0)


def pfas_rules() -> list[Rule]:
    """Return Rule definition for Minnesota Stat. 116.943."""
    return [
        Rule(
            rule_id="MN_PFAS_116_943",
            additive="PFAS",
            aliases=("PTFE", "polytetrafluoroethylene", "PFOA", "PFOS", "fluoroalkyl", "PFAS"),
            jurisdictions=("MN",),
            applies_to=("cosmetic", "food"),
            effective=pfas_effective(),
            clause_ref="Minn. Stat. 116.943 Subd. 5",
            source_text="Beginning January 1, 2025, a person may not sell in Minnesota cookware, cosmetics, or cleaning products containing intentionally added PFAS.",
        )
    ]


def pfas_in_scope(sku: Sku) -> bool:
    """Return True if SKU's category or name falls into one of the covered MN PFAS categories."""
    if not isinstance(sku, Sku):
        raise TypeError("sku must be a Sku")
    cat = (sku.category + " " + sku.name).lower()
    keywords = ("cookware", "skillet", "pan", "cosmetic", "cleaning", "floss", "carpet", "ski wax", "juvenile")
    return any(k in cat for k in keywords)


def detect_pfas_claim(text: str) -> MatchResult | None:
    """Detect intentionally added PFAS/PTFE chemical names in ingredients/composition text."""
    return find_first_match(text, "PFAS", ("PTFE", "polytetrafluoroethylene", "PFOA", "PFOS", "fluoroalkyl", "PFAS"))


def pfas_rationale(sku: Sku, match: MatchResult | None) -> str:
    """Build a rationale string for Minnesota PFAS evaluation."""
    if match is None:
        return f"No intentionally added PFAS detected in {sku.sku_id}."
    return f"Contains prohibited PFAS substance '{match.match_text}' in covered category '{sku.category}' under Minn. Stat. 116.943 Subd. 5."


def evaluate_pfas(sku: Sku, state: str, at: datetime) -> SkuDecision:
    """Evaluate a SKU under Minn. Stat. 116.943."""
    if not isinstance(sku, Sku):
        raise TypeError("sku must be a Sku")
    if state.strip().upper() != "MN" or at.replace(tzinfo=None) < pfas_effective() or not pfas_in_scope(sku):
        return SkuDecision(sku.sku_id, Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, "Outside MN PFAS jurisdiction, date, or product category.")
    m = detect_pfas_claim(sku.ingredients)
    if m is not None:
        return SkuDecision(
            sku_id=sku.sku_id,
            verdict=Verdict.PULL,
            additive="PFAS",
            match_text=m.match_text,
            match_start=m.start,
            match_end=m.end,
            rule_ids=("MN_PFAS_116_943",),
            decided_by=DecidedBy.RULE,
            rationale=pfas_rationale(sku, m),
        )
    return SkuDecision(sku.sku_id, Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, pfas_rationale(sku, None))


def pfas_evidence(sku: Sku, match: MatchResult) -> dict:
    """Build an evidence record dictionary for a Minnesota PFAS match."""
    return {
        "evidence_id": make_evidence_id(sku.sku_id, "MN_PFAS_116_943"),
        "sku_id": sku.sku_id,
        "rule_id": "MN_PFAS_116_943",
        "clause_ref": "Minn. Stat. 116.943 Subd. 5",
        "source_span": [match.start, match.end],
        "rationale": pfas_rationale(sku, match),
        "src": "recallstorm/rules/pfas_mn.py",
    }


def pfas_summary(decisions: list[SkuDecision]) -> dict:
    """Summarize Minnesota PFAS evaluation results."""
    pulled = [d.sku_id for d in decisions if d.verdict == Verdict.PULL and d.additive == "PFAS"]
    return {"rule_id": "MN_PFAS_116_943", "pulled_count": len(pulled), "pulled_skus": pulled}
