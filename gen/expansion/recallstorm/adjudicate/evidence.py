"""Evidence record construction, source span excerpts, and validation for plan.jsonl."""
from __future__ import annotations

from contract import Rule, Sku, SkuDecision, Verdict
from recallstorm.core.ids import make_evidence_id
from recallstorm.core.jsonl import record_with_src, validate_record


def evidence_span(decision: SkuDecision) -> list[int]:
    """Return [start, end] character offsets from a SkuDecision."""
    if decision.match_start is not None and decision.match_end is not None:
        return [decision.match_start, decision.match_end]
    return [0, 0]


def source_excerpt(text: str, start: int, end: int, context: int = 20) -> str:
    """Return an excerpt of text around [start, end) with surrounding context."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    lo = max(0, start - context)
    hi = min(len(text), end + context)
    return text[lo:hi]


def highlight_match(text: str, start: int, end: int) -> str:
    """Highlight the span [start, end) inside text using brackets."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if start < 0 or end < start or end > len(text):
        raise ValueError("Invalid span bounds for text")
    return f"{text[:start]}[{text[start:end]}]{text[end:]}"


def build_evidence(sku: Sku, decision: SkuDecision, rule: Rule) -> dict:
    """Construct a validated 'evidence' plan.jsonl record dictionary."""
    if not isinstance(sku, Sku) or not isinstance(decision, SkuDecision) or not isinstance(rule, Rule):
        raise TypeError("Expected Sku, SkuDecision, and Rule")
    ev_id = make_evidence_id(sku.sku_id, rule.rule_id)
    payload = {
        "evidence_id": ev_id,
        "sku_id": sku.sku_id,
        "rule_id": rule.rule_id,
        "clause_ref": rule.clause_ref,
        "source_span": evidence_span(decision),
        "rationale": decision.rationale,
    }
    return record_with_src(payload, "evidence", "recallstorm/adjudicate/evidence.py")


def evidence_card(sku: Sku, decision: SkuDecision, rule: Rule) -> dict:
    """Build an enriched evidence card including excerpt and highlighted match."""
    rec = build_evidence(sku, decision, rule)
    s, e = rec["source_span"]
    rec["excerpt"] = source_excerpt(sku.ingredients, s, e) if e > s else sku.ingredients[:40]
    rec["highlighted"] = highlight_match(sku.ingredients, s, e) if e > s else sku.ingredients
    return rec


def evidence_to_record(ev: dict) -> dict:
    """Strip extra display fields and return a strict PLAN_TYPES 'evidence' record."""
    payload = {
        "evidence_id": ev["evidence_id"],
        "sku_id": ev["sku_id"],
        "rule_id": ev["rule_id"],
        "clause_ref": ev["clause_ref"],
        "source_span": list(ev["source_span"]),
        "rationale": ev["rationale"],
    }
    return record_with_src(payload, "evidence", "recallstorm/adjudicate/evidence.py")


def link_evidence(
    decisions: dict[str, SkuDecision] | list[SkuDecision],
    rules_by_id: dict[str, Rule],
    skus_by_id: dict[str, Sku],
) -> dict[str, dict]:
    """Build evidence records for all non-KEEP decisions, keyed by sku_id."""
    dlist = list(decisions.values()) if isinstance(decisions, dict) else decisions
    out: dict[str, dict] = {}
    for dec in dlist:
        if dec.verdict == Verdict.KEEP or not dec.rule_ids:
            continue
        rid = dec.rule_ids[0]
        if rid in rules_by_id and dec.sku_id in skus_by_id:
            out[dec.sku_id] = build_evidence(skus_by_id[dec.sku_id], dec, rules_by_id[rid])
    return out


def evidence_index(evidences: list[dict]) -> dict[str, dict]:
    """Index evidence records by evidence_id."""
    return {ev["evidence_id"]: ev for ev in evidences if "evidence_id" in ev}


def validate_evidence(ev: dict) -> list[str]:
    """Validate an evidence record against PLAN_TYPES['evidence']."""
    issues = validate_record(ev, "evidence")
    span = ev.get("source_span")
    if not isinstance(span, list) or len(span) != 2 or span[1] < span[0]:
        issues.append("Invalid source_span")
    return issues
