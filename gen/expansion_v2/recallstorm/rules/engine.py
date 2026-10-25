"""Core rule engine implementing evaluate_sku from contract.py."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from contract import Classifier, DataPack, DecidedBy, Rule, Sku, SkuDecision, Verdict
from recallstorm.aliases.bundles import bundle_match_path, is_bundle
from recallstorm.aliases.detect import find_first_match
from recallstorm.aliases.unclear import needs_human_review, unclear_reason
from recallstorm.core.ids import make_evidence_id
from recallstorm.rules.scope import applies_to_sku

_VERDICT_PRIORITY = {Verdict.PULL: 3, Verdict.HOLD_VERIFY: 2, Verdict.KEEP: 1}


@dataclass
class RuleEngine:
    """Stateful wrapper around evaluate_sku and evaluate_many."""

    rules: list[Rule]
    state: str = "CA"
    classifier: Classifier | None = None

    def evaluate(self, sku: Sku, at: datetime) -> SkuDecision:
        return evaluate_sku(sku, self.rules, self.state, at, classifier=self.classifier)


def evaluate_sku(
    sku: Sku,
    rules: list[Rule],
    state: str,
    at: datetime,
    classifier: Classifier | None = None,
) -> SkuDecision:
    """Evaluate a Sku against rules in state at datetime 'at'.

    Implements the contract.py signature:
      evaluate_sku(sku, rules, state, at, classifier=None) -> SkuDecision
    """
    if not isinstance(sku, Sku):
        raise TypeError("sku must be a Sku instance")
    if not isinstance(at, datetime):
        raise TypeError("at must be a datetime instance")

    applicable_rules = [r for r in rules if applies_to_sku(r, sku, state, at)]
    if not applicable_rules:
        return SkuDecision(
            sku_id=sku.sku_id,
            verdict=Verdict.KEEP,
            additive=None,
            match_text=None,
            match_start=None,
            match_end=None,
            rule_ids=(),
            decided_by=DecidedBy.RULE,
            rationale=f"No rules active in {state} at {at.isoformat()} apply to SKU {sku.sku_id}.",
        )

    # Group applicable rules by additive in order of appearance
    by_additive: dict[str, list[Rule]] = {}
    for r in applicable_rules:
        by_additive.setdefault(r.additive, []).append(r)

    for additive, add_rules in by_additive.items():
        combined_aliases: list[str] = []
        for r in add_rules:
            for al in r.aliases:
                if al not in combined_aliases:
                    combined_aliases.append(al)
        alias_tuple = tuple(combined_aliases)

        if is_bundle(sku.ingredients, sku.category):
            b_hit = bundle_match_path(sku.ingredients, alias_tuple, additive=additive)
            if b_hit is not None:
                comp_name, m = b_hit
                rids = tuple(r.rule_id for r in add_rules)
                return SkuDecision(
                    sku_id=sku.sku_id,
                    verdict=Verdict.PULL,
                    additive=additive,
                    match_text=m.match_text,
                    match_start=m.start,
                    match_end=m.end,
                    rule_ids=rids,
                    decided_by=DecidedBy.RULE,
                    rationale=f"Bundle component {comp_name!r} contains {additive} ({m.match_text!r}) under {', '.join(rids)}.",
                )

        m = find_first_match(sku.ingredients, alias_tuple, additive=additive)
        if m is not None:
            rids = tuple(r.rule_id for r in add_rules)
            return SkuDecision(
                sku_id=sku.sku_id,
                verdict=Verdict.PULL,
                additive=additive,
                match_text=m.match_text,
                match_start=m.start,
                match_end=m.end,
                rule_ids=rids,
                decided_by=DecidedBy.RULE,
                rationale=f"Detected {additive} via {m.match_text!r} at [{m.start}:{m.end}] under {', '.join(rids)}.",
            )

    # If no explicit additive match was found, check whether the label is ambiguous/unreadable
    if needs_human_review(sku.ingredients):
        if classifier is not None:
            return classifier(sku, applicable_rules)
        reason = unclear_reason(sku.ingredients) or "Ambiguous or unreadable ingredient statement"
        rids = tuple(r.rule_id for r in applicable_rules)
        return SkuDecision(
            sku_id=sku.sku_id,
            verdict=Verdict.HOLD_VERIFY,
            additive=applicable_rules[0].additive,
            match_text=None,
            match_start=None,
            match_end=None,
            rule_ids=rids,
            decided_by=DecidedBy.RULE,
            rationale=reason,
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
        rationale=f"Ingredients verified clear of regulated additives ({', '.join(by_additive.keys())}).",
    )


def evaluate_many(
    skus: list[Sku],
    rules: list[Rule],
    state: str,
    at: datetime,
    classifier: Classifier | None = None,
) -> list[SkuDecision]:
    """Evaluate a list of Skus deterministically."""
    return [evaluate_sku(s, rules, state, at, classifier=classifier) for s in skus]


def evaluate_pack(
    pack: DataPack,
    state: str,
    at: datetime | None = None,
    classifier: Classifier | None = None,
) -> dict[str, SkuDecision]:
    """Evaluate all SKUs in a DataPack and return a dict of sku_id -> SkuDecision."""
    eval_time = at or pack.as_of
    return {s.sku_id: evaluate_sku(s, pack.rules, state, eval_time, classifier=classifier) for s in pack.skus}


def stricter_decision(d1: SkuDecision, d2: SkuDecision) -> SkuDecision:
    """Internal helper returning the stricter of two SkuDecisions (PULL > HOLD_VERIFY > KEEP)."""
    if _VERDICT_PRIORITY[d1.verdict] >= _VERDICT_PRIORITY[d2.verdict]:
        return d1
    return d2


def strictest_decision(d1: SkuDecision, d2: SkuDecision) -> SkuDecision:
    """Return the stricter of two SkuDecisions (PULL > HOLD_VERIFY > KEEP)."""
    return stricter_decision(d1, d2)


def merge_decisions(decisions: list[SkuDecision]) -> SkuDecision:
    """Merge multiple SkuDecisions for the same SKU into the strictest combined decision."""
    if not decisions:
        raise ValueError("decisions cannot be empty")
    best = decisions[0]
    all_rules: list[str] = list(best.rule_ids)
    for d in decisions[1:]:
        for rid in d.rule_ids:
            if rid not in all_rules:
                all_rules.append(rid)
        if _VERDICT_PRIORITY[d.verdict] > _VERDICT_PRIORITY[best.verdict]:
            best = d
    if best.verdict == Verdict.KEEP:
        return best
    return SkuDecision(
        sku_id=best.sku_id,
        verdict=best.verdict,
        additive=best.additive,
        match_text=best.match_text,
        match_start=best.match_start,
        match_end=best.match_end,
        rule_ids=tuple(all_rules),
        decided_by=best.decided_by,
        rationale=best.rationale,
    )


def decision_to_record(
    sku: Sku,
    dec: SkuDecision,
    rules: list[Rule],
    evidence_id: str | None = None,
) -> dict:
    """Serialize a SkuDecision to a plan.jsonl 'sku_verdict' record."""
    r_map = {r.rule_id: r for r in rules}
    jurs: list[str] = []
    for rid in dec.rule_ids:
        if rid in r_map:
            for j in r_map[rid].jurisdictions:
                if j not in jurs:
                    jurs.append(j)
    ev_id = evidence_id
    if ev_id is None and dec.rule_ids:
        ev_id = make_evidence_id(sku.sku_id, dec.rule_ids[0])
    match_obj = (
        {"text": dec.match_text, "start": dec.match_start, "end": dec.match_end}
        if dec.match_text is not None
        else None
    )
    return {
        "type": "sku_verdict",
        "sku_id": sku.sku_id,
        "gtin": sku.gtin,
        "verdict": dec.verdict.value,
        "additive": dec.additive,
        "match": match_obj,
        "rule_ids": list(dec.rule_ids),
        "jurisdictions": jurs,
        "decided_by": dec.decided_by.value,
        "evidence_id": ev_id,
        "src": "recallstorm/rules/engine.py",
    }


def decision_counts(decisions: list[SkuDecision]) -> dict[str, int]:
    """Count decisions by Verdict value."""
    counts = {Verdict.PULL.value: 0, Verdict.HOLD_VERIFY.value: 0, Verdict.KEEP.value: 0}
    for d in decisions:
        counts[d.verdict.value] = counts.get(d.verdict.value, 0) + 1
    return counts


def explain_decision(dec: SkuDecision) -> str:
    """Format a SkuDecision as a human-readable explanation."""
    return f"[{dec.verdict.value}] SKU={dec.sku_id} additive={dec.additive} rules={list(dec.rule_ids)}: {dec.rationale}"
