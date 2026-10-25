"""Core regulatory rule engine implementing evaluate_sku from contract.py."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from contract import (
    Classifier,
     DataPack,
    DecidedBy,
    Rule,
    Sku,
    SkuDecision,
    Verdict,
)
from recallstorm.aliases.detect import find_first_match
from recallstorm.aliases.unclear import unclear_reason
from recallstorm.core.jsonl import record_with_src
from recallstorm.rules.dates import effective_at
from recallstorm.rules.jurisdiction import applies_in_state
from recallstorm.rules.scope import sku_in_scope

_VERDICT_PRIORITY = {Verdict.PULL: 3, Verdict.HOLD_VERIFY: 2, Verdict.KEEP: 1}


@dataclass(frozen=True)
class RuleEngine:
    """Stateless wrapper around evaluate_sku and batch evaluation."""

    rules: tuple[Rule, ...]
    state: str = "CA"

    def evaluate(self, sku: Sku, at: datetime, classifier: Classifier | None = None) -> SkuDecision:
        """Evaluate a single SKU."""
        return evaluate_sku(sku, list(self.rules), self.state, at, classifier)


def evaluate_sku(
    sku: Sku,
    rules: list[Rule],
    state: str,
    at: datetime,
    classifier: Classifier | None = None,
) -> SkuDecision:
    """Evaluate a SKU against rules for state and instant `at`.

    Follows contract.py signature and semantics:
    - Rule.effective is compared against local(at) (at.replace(tzinfo=None)).
    - Applies rules whose jurisdictions include `state` or 'US' and whose applies_to matches sku.
    - Returns PULL with exact match_text, match_start, match_end when an active additive alias matches.
    - Returns HOLD_VERIFY when label is vague/unreadable (or delegates to classifier if provided).
    - Returns KEEP otherwise.
    """
    if not isinstance(sku, Sku):
        raise TypeError("sku must be a Sku")
    if not isinstance(rules, list):
        raise TypeError("rules must be a list of Rule objects")
    if not isinstance(state, str) or not state.strip():
        raise ValueError("state must be a non-empty string")
    if not isinstance(at, datetime):
        raise TypeError("at must be a datetime")

    active_rules = [
        r for r in rules
        if applies_in_state(r, state) and sku_in_scope(sku, r) and effective_at(r, at)
    ]
    if not active_rules:
        return SkuDecision(
            sku_id=sku.sku_id,
            verdict=Verdict.KEEP,
            additive=None,
            match_text=None,
            match_start=None,
            match_end=None,
            rule_ids=(),
            decided_by=DecidedBy.RULE,
            rationale=f"No active rules in {state} cover {sku.sku_id} at {at.isoformat()}.",
        )

    by_additive: dict[str, list[Rule]] = {}
    for r in active_rules:
        by_additive.setdefault(r.additive.upper(), []).append(r)

    for additive in sorted(by_additive.keys()):
        add_rules = by_additive[additive]
        extra_aliases: list[str] = []
        for r in add_rules:
            extra_aliases.extend(r.aliases)
        match = find_first_match(sku.ingredients, additive, extra_aliases)
        if match is not None:
            rids = tuple(sorted(r.rule_id for r in add_rules))
            clauses = ", ".join(sorted({r.clause_ref for r in add_rules}))
            return SkuDecision(
                sku_id=sku.sku_id,
                verdict=Verdict.PULL,
                additive=additive,
                match_text=match.match_text,
                match_start=match.start,
                match_end=match.end,
                rule_ids=rids,
                decided_by=DecidedBy.RULE,
                rationale=(
                    f"Ingredient '{match.match_text}' at [{match.start}:{match.end}] "
                    f"matches prohibited additive {additive} under {clauses}."
                ),
            )

    ureason = unclear_reason(sku.ingredients)
    if ureason is not None:
        if classifier is not None:
            return classifier(sku, active_rules)
        rids = tuple(sorted(r.rule_id for r in active_rules))
        primary_add = active_rules[0].additive
        return SkuDecision(
            sku_id=sku.sku_id,
            verdict=Verdict.HOLD_VERIFY,
            additive=primary_add,
            match_text=None,
            match_start=None,
            match_end=None,
            rule_ids=rids,
            decided_by=DecidedBy.RULE,
            rationale=ureason,
        )

    return SkuDecision(
        sku_id=sku.sku_id,
        verdict=Verdict.KEEP,
        additive=None,
        match_text=None,
        match_start=None,
        match_end=None,
        rule_ids=(),
        decided_by=DecidedBy.RULE,
        rationale=f"No prohibited additives detected in {sku.sku_id}.",
    )


def evaluate_many(
    skus: list[Sku],
    rules: list[Rule],
    state: str,
    at: datetime,
    classifier: Classifier | None = None,
) -> list[SkuDecision]:
    """Evaluate a list of SKUs deterministically."""
    return [evaluate_sku(s, rules, state, at, classifier) for s in skus]


def evaluate_pack(
    pack: DataPack,
    state: str = "CA",
    at: datetime | None = None,
    classifier: Classifier | None = None,
) -> dict[str, SkuDecision]:
    """Evaluate all SKUs in a DataPack and return a dict mapping sku_id -> SkuDecision."""
    eval_at = at or pack.as_of
    return {s.sku_id: evaluate_sku(s, pack.rules, state, eval_at, classifier) for s in pack.skus}


def strictest_decision(d1: SkuDecision, d2: SkuDecision) -> SkuDecision:
    """Return the stricter of two SkuDecisions (PULL > HOLD_VERIFY > KEEP)."""
    if _VERDICT_PRIORITY[d2.verdict] > _VERDICT_PRIORITY[d1.verdict]:
        return d2
    return d1


def merge_decisions(decisions: list[SkuDecision]) -> SkuDecision:
    """Merge multiple decisions for the same SKU into a single combined decision."""
    if not decisions:
        raise ValueError("decisions cannot be empty")
    best = decisions[0]
    all_rules: list[str] = list(best.rule_ids)
    for d in decisions[1:]:
        for rid in d.rule_ids:
            if rid not in all_rules:
                all_rules.append(rid)
        best = strictest_decision(best, d)
    return SkuDecision(
        sku_id=best.sku_id,
        verdict=best.verdict,
        additive=best.additive,
        match_text=best.match_text,
        match_start=best.match_start,
        match_end=best.match_end,
        rule_ids=tuple(sorted(all_rules)),
        decided_by=best.decided_by,
        rationale=best.rationale,
    )


def decision_to_record(
    decision: SkuDecision,
    sku: Sku,
    rules: list[Rule],
    evidence_id: str | None = None,
) -> dict:
    """Serialize a SkuDecision to a validated 'sku_verdict' plan.jsonl record."""
    rules_by_id = {r.rule_id: r for r in rules}
    jurs: list[str] = []
    for rid in decision.rule_ids:
        if rid in rules_by_id:
            for j in rules_by_id[rid].jurisdictions:
                if j not in jurs:
                    jurs.append(j)
    match_obj = None
    if decision.match_text is not None and decision.match_start is not None and decision.match_end is not None:
        match_obj = {
            "text": decision.match_text,
            "start": decision.match_start,
            "end": decision.match_end,
        }
    payload = {
        "sku_id": decision.sku_id,
        "gtin": sku.gtin,
        "verdict": decision.verdict.value,
        "additive": decision.additive,
        "match": match_obj,
        "rule_ids": list(decision.rule_ids),
        "jurisdictions": jurs,
        "decided_by": decision.decided_by.value,
        "evidence_id": evidence_id,
    }
    return record_with_src(payload, "sku_verdict", "recallstorm/rules/engine.py")


def decision_counts(decisions: list[SkuDecision] | dict[str, SkuDecision]) -> dict[str, int]:
    """Count PULL, HOLD_VERIFY, and KEEP verdicts."""
    dlist = list(decisions.values()) if isinstance(decisions, dict) else decisions
    counts = {Verdict.PULL.value: 0, Verdict.HOLD_VERIFY.value: 0, Verdict.KEEP.value: 0}
    for d in dlist:
        counts[d.verdict.value] = counts.get(d.verdict.value, 0) + 1
    return counts


def explain_decision(decision: SkuDecision) -> str:
    """Return a concise explanation of a SkuDecision."""
    return f"[{decision.verdict.value}] {decision.sku_id}: {decision.rationale}"
