"""Integration test 05: core -> aliases -> rules -> states -> recall_lots."""
from datetime import datetime
from contract import Sku, Verdict
from recallstorm.aliases.detect import detect_all_additives
from recallstorm.core.ids import make_evidence_id
from recallstorm.recall_lots.fda_notice_parser import detect_undeclared_allergen_type
from recallstorm.recall_lots.lot_pattern_matcher import match_alphanumeric_lot_range
from recallstorm.rules.ab418 import ab418_rules
from recallstorm.rules.engine import evaluate_sku
from recallstorm.states.il_food_safety_act import check_il_sb2637_scope
from recallstorm.states.ny_food_additives import check_ny_ban_date


def test_flow_states_and_lots():
    sku = Sku("S1", "00012345678905", "Bread", "B", "bakery", "WHEAT FLOUR, POTASSIUM BROMATE", True, False, 12, 1.0, 5.0)
    hits = detect_all_additives(sku.ingredients)
    assert any(h.additive == "POTASSIUM_BROMATE" for h in hits)
    dec = evaluate_sku(sku, ab418_rules(), "CA", datetime.fromisoformat("2027-01-01T00:00:00-08:00"))
    assert dec.verdict == Verdict.PULL
    assert check_il_sb2637_scope("POTASSIUM_BROMATE", True)["in_scope"] is True
    assert check_ny_ban_date("2027-02-01")["prohibited"] is True
    assert match_alphanumeric_lot_range("L2605", "L2601", "L2610") is True
    assert detect_undeclared_allergen_type("Undeclared wheat") == "WHEAT"
    assert make_evidence_id(sku.sku_id, "CA_AB418_BROMATE").startswith("EVD-")
