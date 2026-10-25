"""OURS. Hidden acceptance tests for recallstorm.rules.evaluate_sku (contract signature)."""
from __future__ import annotations

import pytest

from conftest import code, la, make_sku, read_jsonl, read_labels

rules_mod = pytest.importorskip("recallstorm.rules")


def evaluate_sku(*a, **kw):
    fn = getattr(rules_mod, "evaluate_sku", None)
    assert fn is not None, "recallstorm.rules must expose evaluate_sku (contract)"
    return fn(*a, **kw)


BANNED = la(2027, 1, 1, 0, 0)          # CA AB 418 effective instant, local
LAST_LEGAL = la(2026, 12, 31, 23, 59)
BASE = "sugar, corn syrup, water, citric acid, natural flavor"

# ---------------------------------------------------------------- labeled data
_SKUS = {r["sku_id"]: r for r in read_jsonl("skus.jsonl")}
_LABELS = read_labels()
_CASES = sorted((s, t) for s, t in _LABELS.items() if s in _SKUS)


def _sku_from_row(r):
    from contract import Sku
    fields = Sku.__dataclass_fields__
    return Sku(**{k: v for k, v in r.items() if k in fields})


@pytest.mark.parametrize("sku_id,truth", _CASES, ids=[c[0] for c in _CASES])
def test_labeled_sku_at_deadline(sku_id, truth, rules):
    d = evaluate_sku(_sku_from_row(_SKUS[sku_id]), rules, "CA", BANNED)
    assert code(d.verdict) == truth, f"{sku_id} {_SKUS[sku_id]['ingredients']!r}: {code(d.verdict)} != {truth}"
    assert d.sku_id == sku_id


def test_labeled_recall_precision(rules):
    tp = fp = fn = 0
    for s, t in _CASES:
        v = code(evaluate_sku(_sku_from_row(_SKUS[s]), rules, "CA", BANNED).verdict)
        tp += t == "PULL" and v == "PULL"; fp += t != "PULL" and v == "PULL"; fn += t == "PULL" and v != "PULL"
    if tp + fn == 0:
        pytest.skip("no PULL labels in data")
    assert tp / (tp + fn) >= 0.90, f"recall {tp}/{tp + fn}"
    assert tp + fp and tp / (tp + fp) >= 0.90, f"precision {tp}/{tp + fp}"


# ---------------------------------------------------------------- aliases
ALIASES = ["FD&C Red No. 3", "Red No. 3", "Red 3", "Red Dye 3", "erythrosine", "E127",
           "FD&C Red #3", "FD&C RED #3", "RED3", "eritrosina", "erythros1ne", "ERYTHROSINE", "red no. 3",
           "F D & C Red No. 3", "FD&C Red No.3 (erythrosine)"]


@pytest.mark.parametrize("alias", ALIASES)
def test_alias_pulled(alias, rules):
    ing = f"{BASE}, {alias}, red 40"
    d = evaluate_sku(make_sku(ing), rules, "CA", BANNED)
    assert code(d.verdict) == "PULL", f"{alias!r} not caught"
    assert d.additive is not None and code(d.additive) == "RED3"
    assert "CA_AB418_RED3" in tuple(d.rule_ids)
    assert code(d.decided_by) == "RULE"


@pytest.mark.parametrize("alias", ["erythrosine", "Red No. 3", "E127"])
def test_match_span_points_into_ingredients(alias, rules):
    ing = f"{BASE}, {alias}, salt"
    d = evaluate_sku(make_sku(ing), rules, "CA", BANNED)
    assert code(d.verdict) == "PULL"
    assert d.match_start is not None and d.match_end is not None
    assert 0 <= d.match_start < d.match_end <= len(ing)
    span = ing[d.match_start:d.match_end].lower()
    assert alias.lower() in span or span in alias.lower(), f"span {span!r} vs {alias!r}"
    if d.match_text is not None:
        assert ing[d.match_start:d.match_end].lower() == d.match_text.lower()


# ---------------------------------------------------------------- decoys
DECOYS = ["Red 40", "FD&C Red No. 40", "D&C Red No. 33", "FD&C Red No. 40 Lake", "Red 33", "3 red apples",
          "red 40 lake, yellow 5"]


@pytest.mark.parametrize("decoy", DECOYS)
def test_decoy_kept(decoy, rules):
    d = evaluate_sku(make_sku(f"{BASE}, {decoy}"), rules, "CA", BANNED)
    assert code(d.verdict) == "KEEP", f"decoy {decoy!r} -> {code(d.verdict)}"


def test_clean_control_kept(rules):
    d = evaluate_sku(make_sku(f"{BASE}, salt"), rules, "CA", BANNED)
    assert code(d.verdict) == "KEEP"


# ---------------------------------------------------------------- unclear labels
@pytest.mark.parametrize("ing", ["artificial color", "artificial colors", "color added", "#####illegible####"])
def test_unclear_held(ing, rules):
    d = evaluate_sku(make_sku(f"{BASE}, {ing}"), rules, "CA", BANNED)
    assert code(d.verdict) == "HOLD_VERIFY", f"{ing!r} -> {code(d.verdict)}"


# ---------------------------------------------------------------- scope: cosmetic, ingested drug
def test_cosmetic_out_of_scope(rules):
    sku = make_sku("castor oil, beeswax, red 3", is_food=False, category="cosmetic")
    for at in (BANNED, la(2027, 2, 1), la(2028, 6, 1)):
        assert code(evaluate_sku(sku, rules, "CA", at).verdict) == "KEEP"


def test_ingested_drug_not_under_food_rule(rules):
    sku = make_sku(f"{BASE}, dextromethorphan, FD&C Red No. 3", is_food=False, is_drug=True,
                   category="cough syrup")
    assert code(evaluate_sku(sku, rules, "CA", BANNED).verdict) == "KEEP"
    assert code(evaluate_sku(sku, rules, "CA", la(2028, 1, 17, 23, 59)).verdict) == "KEEP"


def test_ingested_drug_pulled_after_fda_drug_date(rules):
    sku = make_sku(f"{BASE}, dextromethorphan, FD&C Red No. 3", is_food=False, is_drug=True,
                   category="cough syrup")
    d = evaluate_sku(sku, rules, "CA", la(2028, 1, 18, 0, 0))
    assert code(d.verdict) == "PULL"
    assert "FDA_RED3_DRUG" in tuple(d.rule_ids)
    assert "CA_AB418_RED3" not in tuple(d.rule_ids)


# ---------------------------------------------------------------- dates
def test_last_minute_before_deadline_ok_to_sell(rules):
    d = evaluate_sku(make_sku(f"{BASE}, erythrosine"), rules, "CA", LAST_LEGAL)
    assert code(d.verdict) == "KEEP", "Dec 31 23:59 local is still legal to sell"


def test_deadline_instant_banned(rules):
    d = evaluate_sku(make_sku(f"{BASE}, erythrosine"), rules, "CA", BANNED)
    assert code(d.verdict) == "PULL", "Jan 1 00:00 local is banned (at or after effective)"


def test_one_second_before_deadline(rules):
    from datetime import timedelta
    d = evaluate_sku(make_sku(f"{BASE}, Red No. 3"), rules, "CA", BANNED - timedelta(seconds=1))
    assert code(d.verdict) == "KEEP"


def test_other_state_waits_for_fda_food_date(rules):
    sku = make_sku(f"{BASE}, erythrosine")
    assert code(evaluate_sku(sku, rules, "TX", la(2027, 1, 1)).verdict) == "KEEP"
    d = evaluate_sku(sku, rules, "TX", la(2027, 1, 15, 0, 0))
    assert code(d.verdict) == "PULL"
    assert "FDA_RED3_FOOD" in tuple(d.rule_ids) and "CA_AB418_RED3" not in tuple(d.rule_ids)


def test_ca_after_fda_food_date_cites_rules(rules):
    d = evaluate_sku(make_sku(f"{BASE}, E127"), rules, "CA", la(2027, 2, 1))
    assert code(d.verdict) == "PULL"
    assert "CA_AB418_RED3" in tuple(d.rule_ids)


# ---------------------------------------------------------------- classifier hook + determinism
def test_classifier_not_consulted_for_clear_items(rules):
    calls = []

    def clf(sku, cands):
        calls.append(sku.sku_id)
        from contract import SkuDecision, Verdict, DecidedBy
        return SkuDecision(sku.sku_id, Verdict.HOLD_VERIFY, None, None, None, None, (), DecidedBy.MODEL, "m")
    d1 = evaluate_sku(make_sku(f"{BASE}, erythrosine", sku_id="A"), rules, "CA", BANNED, clf)
    d2 = evaluate_sku(make_sku(f"{BASE}, salt", sku_id="B"), rules, "CA", BANNED, clf)
    assert code(d1.verdict) == "PULL" and code(d1.decided_by) == "RULE"
    assert code(d2.verdict) == "KEEP" and code(d2.decided_by) == "RULE"
    assert "A" not in calls


def test_classifier_used_for_unclear_items(rules):
    from contract import SkuDecision, Verdict, DecidedBy

    def clf(sku, cands):
        return SkuDecision(sku.sku_id, Verdict.HOLD_VERIFY, None, None, None, None, (), DecidedBy.MODEL, "model")
    d = evaluate_sku(make_sku(f"{BASE}, artificial color"), rules, "CA", BANNED, clf)
    assert code(d.verdict) == "HOLD_VERIFY"


def test_deterministic(rules):
    sku = make_sku(f"{BASE}, FD&C Red No. 3")
    assert evaluate_sku(sku, rules, "CA", BANNED) == evaluate_sku(sku, rules, "CA", BANNED)
