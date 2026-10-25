"""Integration test 09: Multilingual aliases, bundles/kits, decoys, and evidence span accuracy."""
from datetime import datetime, timezone
from contract import Sku, Verdict
from recallstorm.adjudicate import build_evidence, highlight_match
from recallstorm.aliases import (
    bundle_match_path,
    classify_red_mention,
    is_bundle,
    translated_match,
)
from recallstorm.core import validate_record
from recallstorm.plan import explain_sku
from recallstorm.rules import decision_to_record, evaluate_sku, red3_rules


def test_flow_09_bundles_decoys_and_spans():
    rules = red3_rules()
    at = datetime(2027, 1, 2, tzinfo=timezone.utc)

    # 1. Bundle kit with Red 3 inside one sub-component
    kit_ing = (
        "KIT CONTAINS: Pretzels: WHEAT FLOUR, SALT, RED 40 LAKE. "
        "| Sprinkles: SUGAR, CORNSTARCH, RED 3 POWDER, CARNAUBA WAX."
    )
    assert is_bundle(kit_ing, "seasonal kits") is True
    path = bundle_match_path(kit_ing, "RED3")
    assert path is not None and path[0] == "Sprinkles"
    kit_sku = Sku("KIT1", "02000000001418", "Candy Kit", "B", "seasonal kits", kit_ing, True, False, 12, 2.0, 5.0)
    kit_dec = evaluate_sku(kit_sku, rules, "CA", at)
    assert kit_dec.verdict == Verdict.PULL
    assert kit_ing[kit_dec.match_start:kit_dec.match_end] == kit_dec.match_text

    ev = build_evidence(kit_sku, kit_dec, rules[0])
    v_rec = decision_to_record(kit_dec, kit_sku, rules, ev["evidence_id"])
    assert validate_record(ev) == []
    assert validate_record(v_rec) == []
    assert "[RED 3 POWDER]" in highlight_match(kit_ing, kit_dec.match_start, kit_dec.match_end)
    assert "PULL" in explain_sku(v_rec, ev)

    # 2. Multilingual Spanish alias
    es_ing = "AZUCAR, JARABE DE MAIZ, ERITROSINA, SAL."
    assert translated_match(es_ing, "RED3") is not None
    es_sku = Sku("ES1", "00012345678905", "Dulce", "B", "candy", es_ing, True, False, 12, 1.0, 5.0)
    es_dec = evaluate_sku(es_sku, rules, "CA", at)
    assert es_dec.verdict == Verdict.PULL and es_dec.match_text == "ERITROSINA"

    # 3. Decoy SKU (Red 40 + 3 Pepper) -> KEEP
    decoy_ing = "BEEF, SPICES (3 RED BELL PEPPERS), FD&C RED #40, D&C RED #33."
    assert classify_red_mention("FD&C RED #40") == "RED40"
    decoy_sku = Sku("DEC1", "00012345678912", "Jerky", "B", "snacks", decoy_ing, True, False, 12, 1.0, 5.0)
    assert evaluate_sku(decoy_sku, rules, "CA", at).verdict == Verdict.KEEP
