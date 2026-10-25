"""CARB multi-purpose lubricant VOC limits evaluation."""
from __future__ import annotations

from datetime import datetime
import re

from contract import DecidedBy, Rule, Sku, SkuDecision, Verdict
from recallstorm.core.ids import make_evidence_id

_VOC_RE = re.compile(r"\bVOC\s*[:=]?\s*(\d+(?:\.\d+)?)\s*%", re.IGNORECASE)


def voc_effective() -> datetime:
    """Return the CARB multi-purpose lubricant VOC limit effective date."""
    return datetime(2025, 1, 1, 0, 0, 0)


def carb_voc_rules() -> list[Rule]:
    """Return the California CARB multi-purpose lubricant VOC Rule."""
    return [
        Rule(
            rule_id="CA_CARB_LUBRICANT_VOC",
            additive="VOC_OVER_LIMIT",
            aliases=("VOC", "volatile organic compounds"),
            jurisdictions=("CA",),
            applies_to=("cosmetic",),
            effective=voc_effective(),
            clause_ref="17 CCR 94509(a) (CARB Consumer Products)",
            source_text="Multi-purpose lubricant products sold in California shall not exceed 25% VOC by weight.",
        )
    ]


def voc_limit_for_category(category: str) -> float:
    """Return the maximum allowable VOC percentage by weight for category in California."""
    cat = (category or "").lower()
    if "lubricant" in cat or "penetrating" in cat:
        return 25.0
    return 50.0


def lubricant_in_scope(sku: Sku) -> bool:
    """Return True if sku is a multi-purpose lubricant product."""
    blob = f"{sku.category} {sku.name}".lower()
    return "lubricant" in blob or "penetrating oil" in blob


def parse_voc_percent(text: str) -> float | None:
    """Extract numeric VOC percentage from text (e.g., 'VOC: 35%')."""
    if not isinstance(text, str):
        return None
    m = _VOC_RE.search(text)
    return float(m.group(1)) if m else None


def voc_rationale(sku: Sku, voc_pct: float | None, limit: float) -> str:
    """Build rationale string for CARB VOC evaluation."""
    if voc_pct is not None and voc_pct > limit:
        return f"SKU {sku.sku_id} has VOC {voc_pct:.1f}% exceeding CARB limit of {limit:.1f}%."
    return f"SKU {sku.sku_id} complies with CARB VOC limit ({limit:.1f}%)."


def voc_evidence(sku: Sku, voc_pct: float) -> dict:
    """Build an evidence record for a CARB VOC violation."""
    limit = voc_limit_for_category(sku.category)
    return {
        "type": "evidence",
        "evidence_id": make_evidence_id(sku.sku_id, "CA_CARB_LUBRICANT_VOC"),
        "sku_id": sku.sku_id,
        "rule_id": "CA_CARB_LUBRICANT_VOC",
        "clause_ref": "17 CCR 94509(a)",
        "source_span": {"start": 0, "end": len(sku.ingredients), "text": f"VOC {voc_pct}%"},
        "rationale": voc_rationale(sku, voc_pct, limit),
        "src": "recallstorm/rules/carb_voc.py",
    }


def evaluate_voc(sku: Sku, state: str, at: datetime) -> SkuDecision:
    """Evaluate a Sku against CARB multi-purpose lubricant VOC limits."""
    wall = at.replace(tzinfo=None)
    limit = voc_limit_for_category(sku.category)
    if state.upper() != "CA" or not lubricant_in_scope(sku) or wall < voc_effective():
        return SkuDecision(sku.sku_id, Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, "Out of scope")
    voc_pct = parse_voc_percent(sku.ingredients)
    if voc_pct is not None and voc_pct > limit:
        m = _VOC_RE.search(sku.ingredients)
        s = m.start() if m else 0
        e = m.end() if m else len(sku.ingredients)
        return SkuDecision(
            sku_id=sku.sku_id,
            verdict=Verdict.PULL,
            additive="VOC_OVER_LIMIT",
            match_text=sku.ingredients[s:e],
            match_start=s,
            match_end=e,
            rule_ids=("CA_CARB_LUBRICANT_VOC",),
            decided_by=DecidedBy.RULE,
            rationale=voc_rationale(sku, voc_pct, limit),
        )
    return SkuDecision(sku.sku_id, Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, voc_rationale(sku, voc_pct, limit))


def voc_summary(decisions: list[SkuDecision]) -> dict:
    """Summarize CARB VOC decisions."""
    pulled = [d.sku_id for d in decisions if d.verdict == Verdict.PULL and d.additive == "VOC_OVER_LIMIT"]
    return {"total": len(decisions), "pulled_count": len(pulled), "pulled_skus": pulled}
