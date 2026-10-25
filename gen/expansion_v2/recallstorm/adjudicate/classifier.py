"""Heuristic and model-based classifiers for unclear labels."""
from __future__ import annotations

from dataclasses import dataclass
import json

from contract import Classifier, DecidedBy, Rule, Sku, SkuDecision, Verdict
from recallstorm.aliases.detect import find_first_match
from recallstorm.aliases.unclear import unclear_reason


@dataclass
class ClassifierStats:
    """Counters for classifier invocations."""

    called: int = 0
    pulls: int = 0
    holds: int = 0
    keeps: int = 0


def confidence_threshold(conf: float, min_conf: float = 0.8) -> bool:
    """Return True if confidence meets or exceeds min_conf."""
    return float(conf) >= float(min_conf)


def fallback_hold(sku: Sku, candidates: list[Rule], reason: str = "Unclear label") -> SkuDecision:
    """Return a safe HOLD_VERIFY SkuDecision when a classifier is unsure."""
    rids = tuple(r.rule_id for r in candidates)
    add = candidates[0].additive if candidates else None
    return SkuDecision(
        sku_id=sku.sku_id,
        verdict=Verdict.HOLD_VERIFY,
        additive=add,
        match_text=None,
        match_start=None,
        match_end=None,
        rule_ids=rids,
        decided_by=DecidedBy.MODEL,
        rationale=reason,
    )


def classifier_decision(sku: Sku, verdict: Verdict, rationale: str, rules: list[Rule]) -> SkuDecision:
    """Construct a DecidedBy.MODEL SkuDecision."""
    rids = tuple(r.rule_id for r in rules) if verdict != Verdict.KEEP else ()
    add = rules[0].additive if (rules and verdict != Verdict.KEEP) else None
    return SkuDecision(
        sku_id=sku.sku_id,
        verdict=verdict,
        additive=add,
        match_text=None,
        match_start=None,
        match_end=None,
        rule_ids=rids,
        decided_by=DecidedBy.MODEL,
        rationale=rationale,
    )


def classifier_prompt(sku: Sku, candidates: list[Rule]) -> str:
    """Build a structured prompt for classifying an ambiguous SKU label."""
    r_str = ", ".join(f"{r.rule_id}({r.additive})" for r in candidates)
    return (
        f"Classify SKU {sku.sku_id} ({sku.name}) against rules [{r_str}]. "
        f"Ingredients: {sku.ingredients!r}. Return JSON with verdict (PULL|HOLD_VERIFY|KEEP) and rationale."
    )


def parse_classifier_reply(reply: str, sku: Sku, candidates: list[Rule]) -> SkuDecision:
    """Parse a JSON or text reply from a classifier into a SkuDecision, falling back to HOLD_VERIFY."""
    if not isinstance(reply, str) or not reply.strip():
        return fallback_hold(sku, candidates, "Empty classifier reply")
    try:
        data = json.loads(reply)
        v_raw = str(data.get("verdict", "HOLD_VERIFY")).upper().strip()
        verdict = Verdict(v_raw)
        conf = float(data.get("confidence", 0.9))
        if not confidence_threshold(conf):
            return fallback_hold(sku, candidates, f"Low confidence ({conf:.2f})")
        return classifier_decision(sku, verdict, str(data.get("rationale", "Model decision")), candidates)
    except Exception:
        return fallback_hold(sku, candidates, "Unparseable classifier reply")


class HeuristicClassifier:
    """Deterministic local classifier implementing the contract.Classifier protocol."""

    def __call__(self, sku: Sku, candidates: list[Rule]) -> SkuDecision:
        for r in candidates:
            m = find_first_match(sku.ingredients, r.aliases, additive=r.additive)
            if m:
                return SkuDecision(
                    sku_id=sku.sku_id,
                    verdict=Verdict.PULL,
                    additive=r.additive,
                    match_text=m.match_text,
                    match_start=m.start,
                    match_end=m.end,
                    rule_ids=(r.rule_id,),
                    decided_by=DecidedBy.MODEL,
                    rationale=f"HeuristicClassifier matched {m.match_text!r}",
                )
        reason = unclear_reason(sku.ingredients)
        if reason:
            return fallback_hold(sku, candidates, reason)
        return classifier_decision(sku, Verdict.KEEP, "HeuristicClassifier verified clean", candidates)


class GeminiClassifier(HeuristicClassifier):
    """Offline-safe GeminiClassifier adapter that falls back to HOLD_VERIFY when unsure."""


def batch_classify(
    skus: list[Sku], rules: list[Rule], classifier: Classifier | None = None
) -> list[SkuDecision]:
    """Classify a batch of SKUs using classifier (or HeuristicClassifier)."""
    clf = classifier or HeuristicClassifier()
    return [clf(s, rules) for s in skus]
