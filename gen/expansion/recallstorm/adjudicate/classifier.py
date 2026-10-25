"""HeuristicClassifier and GeminiClassifier implementing the contract.py Classifier protocol."""
from __future__ import annotations

import json
from dataclasses import dataclass
from contract import DecidedBy, Rule, Sku, SkuDecision, Verdict
from recallstorm.aliases.detect import find_first_match
from recallstorm.aliases.unclear import unclear_reason


@dataclass
class ClassifierStats:
    """Call counters for model/heuristic classifiers."""

    calls: int = 0
    pulls: int = 0
    holds: int = 0
    keeps: int = 0


def classifier_prompt(sku: Sku, candidates: list[Rule]) -> str:
    """Format a structured prompt for Gemini classification of an ambiguous SKU label."""
    rids = ", ".join(r.rule_id for r in candidates)
    additives = ", ".join(sorted({r.additive for r in candidates}))
    return (
        f"Classify SKU {sku.sku_id} ({sku.name}) under rules [{rids}] targeting [{additives}].\n"
        f"Ingredients: {sku.ingredients}\n"
        "Respond with JSON: {\"verdict\": \"PULL|HOLD_VERIFY|KEEP\", \"rationale\": \"...\"}"
    )


def fallback_hold(sku: Sku, candidates: list[Rule], reason: str = "Ambiguous ingredient declaration") -> SkuDecision:
    """Return a safe HOLD_VERIFY SkuDecision with DecidedBy.MODEL."""
    rids = tuple(sorted(r.rule_id for r in candidates))
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


def classifier_decision(
    sku: Sku,
    candidates: list[Rule],
    verdict: Verdict,
    rationale: str,
) -> SkuDecision:
    """Build a SkuDecision emitted by a model classifier."""
    rids = tuple(sorted(r.rule_id for r in candidates)) if verdict != Verdict.KEEP else ()
    add = (candidates[0].additive if candidates else None) if verdict != Verdict.KEEP else None
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


def parse_classifier_reply(reply: str, sku: Sku, candidates: list[Rule]) -> SkuDecision:
    """Parse a JSON reply from Gemini into a SkuDecision, falling back to HOLD_VERIFY."""
    if not isinstance(reply, str) or not reply.strip():
        return fallback_hold(sku, candidates, "Empty classifier response")
    try:
        data = json.loads(reply.strip())
        v_str = str(data.get("verdict", "HOLD_VERIFY")).upper()
        verdict = Verdict(v_str)
        rationale = str(data.get("rationale", "Model classification"))
        return classifier_decision(sku, candidates, verdict, rationale)
    except Exception:
        return fallback_hold(sku, candidates, "Unparseable classifier response")


def confidence_threshold(score: float, threshold: float = 0.85) -> bool:
    """Return True if a classifier confidence score meets or exceeds threshold."""
    if not (0.0 <= threshold <= 1.0):
        raise ValueError("threshold must be in [0.0, 1.0]")
    return score >= threshold


class HeuristicClassifier:
    """Deterministic local classifier implementing the contract.py Classifier protocol."""

    def __init__(self) -> None:
        self.stats = ClassifierStats()

    def __call__(self, sku: Sku, candidates: list[Rule]) -> SkuDecision:
        self.stats.calls += 1
        for r in candidates:
            m = find_first_match(sku.ingredients, r.additive, r.aliases)
            if m is not None:
                self.stats.pulls += 1
                return SkuDecision(
                    sku_id=sku.sku_id,
                    verdict=Verdict.PULL,
                    additive=r.additive,
                    match_text=m.match_text,
                    match_start=m.start,
                    match_end=m.end,
                    rule_ids=(r.rule_id,),
                    decided_by=DecidedBy.MODEL,
                    rationale=f"Classifier detected {r.additive} ('{m.match_text}').",
                )
        ureason = unclear_reason(sku.ingredients)
        if ureason is not None:
            self.stats.holds += 1
            return fallback_hold(sku, candidates, ureason)
        self.stats.keeps += 1
        return classifier_decision(sku, candidates, Verdict.KEEP, "Classifier verified no prohibited additive.")


class GeminiClassifier:
    """Configurable Gemini classifier with offline fallback to HeuristicClassifier."""

    def __init__(self, responder=None) -> None:
        self.responder = responder
        self.heuristic = HeuristicClassifier()

    def __call__(self, sku: Sku, candidates: list[Rule]) -> SkuDecision:
        if self.responder is not None:
            prompt = classifier_prompt(sku, candidates)
            reply = self.responder(prompt)
            return parse_classifier_reply(reply, sku, candidates)
        return self.heuristic(sku, candidates)


def batch_classify(skus: list[Sku], candidates: list[Rule], classifier=None) -> list[SkuDecision]:
    """Classify a batch of SKUs with the provided classifier."""
    clf = classifier or HeuristicClassifier()
    return [clf(s, candidates) for s in skus]
