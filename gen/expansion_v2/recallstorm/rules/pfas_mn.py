"""Minnesota PFAS Statute 116.943 (Amara's Law) product evaluation."""
from __future__ import annotations

from datetime import datetime

from contract import DecidedBy, Rule, Sku, SkuDecision, Verdict
from recallstorm.aliases.detect import MatchResult, find_first_match
from recallstorm.core.ids import make_evidence_id

_PFAS_CATEGORIES: tuple[str, ...] = (
    "cookware",
    "carpets",
    "rugs",
    "cleaning products",
    "cosmetics",
    "dental floss",
    "fabric treatments",
    "juvenile products",
    "menstruation products",
    "textile furnishings",
    "ski wax",
    "upholstered furniture",
)

_PFAS_ALIASES: tuple[str, ...] = (
    "PFAS",
    "PTFE",
    "polytetrafluoroethylene",
    "perfluoroalkyl",
    "polyfluoroalkyl",
    "PFOA",
    "PFOS",
    "fluoro-treated",
)


def pfas_product_categories() -> tuple[str, ...]:
    """Return the 11+ product categories regulated under Minnesota Stat. 116.943 Subd. 5 (2025)."""
    return _PFAS_CATEGORIES


def pfas_effective() -> datetime:
    """Return the naive local effective date for Minnesota Stat. 116.943 Subd. 5 (2025-01-01)."""
    return datetime(2025, 1, 1, 0, 0, 0)


def pfas_rules() -> list[Rule]:
    """Return the Minnesota PFAS 116.943 Rule."""
    return [
        Rule(
            rule_id="MN_PFAS_116_943",
            additive="PFAS",
            aliases=_PFAS_ALIASES,
            jurisdictions=("MN",),
            applies_to=("cosmetic", "food"),
            effective=pfas_effective(),
            clause_ref="Minn. Stat. 116.943 Subd. 5",
            source_text="Beginning January 1, 2025, a person may not sell, offer for sale, or distribute for sale in Minnesota cookware, cosmetics, dental floss, juvenile products, or fabric treatments containing intentionally added PFAS.",
        )
    ]


def pfas_in_scope(sku: Sku) -> bool:
    """Return True if sku's category or name falls within Minnesota Stat. 116.943 categories."""
    blob = f"{sku.category} {sku.name}".lower()
    return any(cat in blob for cat in _PFAS_CATEGORIES) or any(
        k in blob for k in ("pan", "skillet", "nonstick", "floss", "cosmetic", "carpet", "wax")
    )


def detect_pfas_claim(text: str) -> MatchResult | None:
    """Detect intentionally added PFAS / PTFE substances in text."""
    if "pfas-free" in (text or "").lower() or "pfoa-free" in (text or "").lower():
        return None
    return find_first_match(text, _PFAS_ALIASES, additive="PFAS")


def pfas_rationale(sku: Sku, match: MatchResult | None) -> str:
    """Build rationale string for Minnesota PFAS 116.943 evaluation."""
    if match:
        return f"SKU {sku.sku_id} contains intentionally added PFAS ({match.match_text!r}) prohibited under Minn. Stat. 116.943."
    return f"SKU {sku.sku_id} does not contain prohibited PFAS under Minn. Stat. 116.943."


def pfas_evidence(sku: Sku, match: MatchResult) -> dict:
    """Build an evidence record for a Minnesota PFAS match."""
    return {
        "type": "evidence",
        "evidence_id": make_evidence_id(sku.sku_id, "MN_PFAS_116_943"),
        "sku_id": sku.sku_id,
        "rule_id": "MN_PFAS_116_943",
        "clause_ref": "Minn. Stat. 116.943 Subd. 5",
        "source_span": {"start": match.start, "end": match.end, "text": match.match_text},
        "rationale": pfas_rationale(sku, match),
        "src": "recallstorm/rules/pfas_mn.py",
    }


def evaluate_pfas(sku: Sku, state: str, at: datetime) -> SkuDecision:
    """Evaluate a Sku against Minnesota Stat. 116.943 PFAS prohibition."""
    wall = at.replace(tzinfo=None)
    if state.upper() != "MN" or not pfas_in_scope(sku) or wall < pfas_effective():
        return SkuDecision(sku.sku_id, Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, "Out of scope or pre-effective")
    m = detect_pfas_claim(sku.ingredients)
    if m:
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


def pfas_summary(decisions: list[SkuDecision]) -> dict:
    """Summarize Minnesota PFAS decisions."""
    pulled = [d.sku_id for d in decisions if d.verdict == Verdict.PULL and d.additive == "PFAS"]
    return {"total": len(decisions), "pulled_count": len(pulled), "pulled_skus": pulled}
