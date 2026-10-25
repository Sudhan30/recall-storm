"""CARB Consumer Products Regulation (17 CCR 94509) multi-purpose lubricant VOC limit evaluation."""
from __future__ import annotations

import re
from datetime import datetime
from contract import DecidedBy, Rule, Sku, SkuDecision, Verdict
from recallstorm.core.ids import make_evidence_id

_VOC_RE = re.compile(r"\bVOC\s*[:=]?\s*(\d+(?:\.\d+)?)\s*%", re.IGNORECASE)


def voc_effective() -> datetime:
    """Return effective datetime for CARB multi-purpose lubricant 10% VOC standard."""
    return datetime(2026, 1, 1, 0, 0, 0)


def voc_limit_for_category(category: str) -> float:
    """Return maximum allowed VOC weight percent for a consumer product category."""
    cat = category.strip().lower()
    if "lubricant" in cat:
        return 10.0
    if "degreaser" in cat:
        return 10.0
    return 25.0


def carb_voc_rules() -> list[Rule]:
    """Return CARB VOC Rule definition."""
    return [
        Rule(
            rule_id="CARB_LUBRICANT_VOC",
            additive="VOC_EXCEEDANCE",
            aliases=("VOC > 10%",),
            jurisdictions=("CA",),
            applies_to=("cosmetic",),
            effective=voc_effective(),
            clause_ref="17 CCR 94509(a)",
            source_text="Multi-purpose lubricants sold in California shall not exceed 10% VOC by weight.",
        )
    ]


def parse_voc_percent(text: str) -> float | None:
    """Extract numeric VOC weight percentage from product label text."""
    if not isinstance(text, str):
        return None
    m = _VOC_RE.search(text)
    if not m:
        return None
    return float(m.group(1))


def lubricant_in_scope(sku: Sku) -> bool:
    """Return True if SKU is a multi-purpose lubricant."""
    if not isinstance(sku, Sku):
        raise TypeError("sku must be a Sku")
    text = (sku.category + " " + sku.name).lower()
    return "lubricant" in text


def voc_rationale(sku: Sku, voc_pct: float | None, limit: float = 10.0) -> str:
    """Build a rationale string for CARB VOC evaluation."""
    if voc_pct is None:
        return f"No VOC percentage declared on {sku.sku_id}."
    if voc_pct > limit:
        return f"Declared VOC {voc_pct}% exceeds CARB limit of {limit}% under 17 CCR 94509(a)."
    return f"Declared VOC {voc_pct}% is within CARB limit of {limit}%."


def evaluate_voc(sku: Sku, state: str, at: datetime) -> SkuDecision:
    """Evaluate a lubricant SKU against CARB VOC limits."""
    if not isinstance(sku, Sku):
        raise TypeError("sku must be a Sku")
    if state.strip().upper() != "CA" or at.replace(tzinfo=None) < voc_effective() or not lubricant_in_scope(sku):
        return SkuDecision(sku.sku_id, Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, "Outside CARB VOC scope.")
    limit = voc_limit_for_category(sku.category)
    m = _VOC_RE.search(sku.ingredients)
    if m is None:
        return SkuDecision(sku.sku_id, Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, voc_rationale(sku, None, limit))
    pct = float(m.group(1))
    if pct > limit:
        return SkuDecision(
            sku_id=sku.sku_id,
            verdict=Verdict.PULL,
            additive="VOC_EXCEEDANCE",
            match_text=m.group(0),
            match_start=m.start(),
            match_end=m.end(),
            rule_ids=("CARB_LUBRICANT_VOC",),
            decided_by=DecidedBy.RULE,
            rationale=voc_rationale(sku, pct, limit),
        )
    return SkuDecision(sku.sku_id, Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, voc_rationale(sku, pct, limit))


def voc_evidence(sku: Sku, voc_pct: float) -> dict:
    """Build an evidence dictionary for a CARB VOC exceedance."""
    m = _VOC_RE.search(sku.ingredients)
    span = [m.start(), m.end()] if m else [0, 0]
    return {
        "evidence_id": make_evidence_id(sku.sku_id, "CARB_LUBRICANT_VOC"),
        "sku_id": sku.sku_id,
        "rule_id": "CARB_LUBRICANT_VOC",
        "clause_ref": "17 CCR 94509(a)",
        "source_span": span,
        "rationale": voc_rationale(sku, voc_pct, voc_limit_for_category(sku.category)),
        "src": "recallstorm/rules/carb_voc.py",
    }


def voc_summary(decisions: list[SkuDecision]) -> dict:
    """Summarize CARB VOC evaluation decisions."""
    pulled = [d.sku_id for d in decisions if d.verdict == Verdict.PULL and d.additive == "VOC_EXCEEDANCE"]
    return {"rule_id": "CARB_LUBRICANT_VOC", "pulled_count": len(pulled), "pulled_skus": pulled}
