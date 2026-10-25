"""Build and validate evidence records for plan.jsonl."""
from __future__ import annotations

from contract import Rule, Sku, SkuDecision
from recallstorm.core.ids import make_evidence_id
from recallstorm.core.jsonl import validate_record


def source_excerpt(text: str, start: int | None, end: int | None, context: int = 20) -> str:
    """Return a snippet of text surrounding [start, end) with context characters."""
    if not isinstance(text, str) or not text:
        return ""
    if start is None or end is None:
        return text[: min(len(text), context * 2)]
    s = max(0, start - context)
    e = min(len(text), end + context)
    return text[s:e]


def highlight_match(text: str, start: int | None, end: int | None) -> str:
    """Highlight [start, end) in text using [MATCH: ...]."""
    if not isinstance(text, str) or start is None or end is None:
        return text or ""
    return f"{text[:start]}[{text[start:end]}]{text[end:]}"


def evidence_span(sku: Sku, dec: SkuDecision) -> dict:
    """Build the source_span dictionary for an evidence record."""
    if dec.match_start is not None and dec.match_end is not None:
        return {
            "start": dec.match_start,
            "end": dec.match_end,
            "text": sku.ingredients[dec.match_start : dec.match_end],
        }
    return {"start": 0, "end": len(sku.ingredients), "text": source_excerpt(sku.ingredients, None, None, 40)}


def build_evidence(sku: Sku, dec: SkuDecision, rule: Rule) -> dict:
    """Build a plan.jsonl 'evidence' record for a SkuDecision and Rule."""
    ev_id = make_evidence_id(sku.sku_id, rule.rule_id)
    return {
        "type": "evidence",
        "evidence_id": ev_id,
        "sku_id": sku.sku_id,
        "rule_id": rule.rule_id,
        "clause_ref": rule.clause_ref,
        "source_span": evidence_span(sku, dec),
        "rationale": dec.rationale,
        "src": "recallstorm/adjudicate/evidence.py",
    }


def evidence_to_record(ev: dict) -> dict:
    """Ensure an evidence dict has 'type' and 'src' fields set."""
    out = dict(ev)
    out["type"] = "evidence"
    out.setdefault("src", "recallstorm/adjudicate/evidence.py")
    return out


def evidence_card(ev: dict) -> str:
    """Render a compact text card for an evidence record."""
    span = ev.get("source_span") or {}
    return f"Evidence {ev.get('evidence_id')}: SKU={ev.get('sku_id')} Rule={ev.get('rule_id')} ({ev.get('clause_ref')}) Span={span.get('text')!r}"


def link_evidence(verdict_rec: dict, ev_rec: dict) -> dict:
    """Attach ev_rec['evidence_id'] to a sku_verdict record."""
    out = dict(verdict_rec)
    out["evidence_id"] = ev_rec["evidence_id"]
    return out


def evidence_index(ev_records: list[dict]) -> dict[str, dict]:
    """Index evidence records by evidence_id."""
    return {r["evidence_id"]: r for r in ev_records if "evidence_id" in r}


def validate_evidence(ev: dict) -> list[str]:
    """Validate an evidence record against PLAN_TYPES['evidence']."""
    return validate_record(ev, "evidence")
