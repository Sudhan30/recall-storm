"""Unit tests for recallstorm.gs1.match."""
from contract import Sku
from recallstorm.gs1.match import (
    GtinIndex,
    best_match,
    match_by_gtin,
    match_by_lot,
    match_by_name,
    match_recall_to_skus,
    match_report,
    match_score,
    unmatched_recalls,
)


def test_gs1_match():
    s1 = Sku("FDC1034191", "07502264930572", "Rainbow Sprinkles", "Nayarit", "baking", "RED 3", True, False, 6, 2.0, 10.0)
    s2 = Sku("FDC1913788", "00811033712026", "Maraschino Cherries", "Bell", "baking", "RED 40", True, False, 12, 1.4, 4.6)
    skus = [s1, s2]

    idx = GtinIndex.from_skus(skus)
    assert "07502264930572" in idx.by_gtin
    assert match_by_gtin("07502264930572", skus) == [s1]
    assert match_by_lot("L26*", {"FDC1034191": ["L2601"], "FDC1913788": ["B99"]}) == ["FDC1034191"]
    assert match_by_name("Nayarit Rainbow Sprinkles", skus) == [s1]

    rec = {"recall_id": "R1", "gtins": ["07502264930572"], "title": "Rainbow Sprinkles"}
    assert match_score(rec, s1) == 1.0
    assert match_recall_to_skus(rec, skus) == [s1]
    assert best_match(rec, skus) == s1
    rec_unmatched = {"recall_id": "R2", "gtins": ["00000000000000"], "title": "Unrelated Item"}
    assert len(unmatched_recalls([rec, rec_unmatched], skus)) == 1
    rep = match_report([rec, rec_unmatched], skus)
    assert rep["matched_recalls"] == 1 and rep["unmatched_recalls"] == 1
