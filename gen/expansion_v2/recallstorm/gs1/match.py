"""Match recall notices to SKUs by GTIN, lot, and product name."""
from __future__ import annotations

from dataclasses import dataclass, field

from contract import Sku
from recallstorm.gs1.gtin import normalize_gtin
from recallstorm.gs1.lots import lot_matches_recall


@dataclass
class GtinIndex:
    """Fast lookup index from normalized GTIN-14 to Skus."""

    by_gtin: dict[str, list[Sku]] = field(default_factory=dict)

    @classmethod
    def from_skus(cls, skus: list[Sku]) -> GtinIndex:
        idx = cls()
        for s in skus:
            try:
                g = normalize_gtin(s.gtin)
            except Exception:
                g = s.gtin.zfill(14)
            idx.by_gtin.setdefault(g, []).append(s)
        return idx


def match_by_gtin(gtin: str, skus: list[Sku]) -> list[Sku]:
    """Return all Skus matching the normalized 14-digit GTIN."""
    try:
        target = normalize_gtin(gtin)
    except Exception:
        target = gtin.strip().zfill(14)
    return [s for s in skus if s.gtin.zfill(14) == target]


def match_by_lot(lot: str, sku_lots: dict[str, list[str]]) -> list[str]:
    """Return sku_ids whose lot list matches the target recall lot specification."""
    out: list[str] = []
    for sku_id, lots in sku_lots.items():
        if any(lot_matches_recall(l, [lot]) for l in lots):
            out.append(sku_id)
    return sorted(out)


def match_by_name(name: str, skus: list[Sku], threshold: float = 0.5) -> list[Sku]:
    """Match Skus by token overlap between name and Sku.name + Sku.brand."""
    q_tokens = {t.lower() for t in (name or "").split() if len(t) > 2}
    if not q_tokens:
        return []
    out: list[Sku] = []
    for s in skus:
        s_tokens = {t.lower().strip(",.") for t in f"{s.brand} {s.name}".split() if len(t) > 2}
        if not s_tokens:
            continue
        overlap = len(q_tokens & s_tokens) / max(1, min(len(q_tokens), len(s_tokens)))
        if overlap >= threshold:
            out.append(s)
    return out


def match_score(recall: dict, sku: Sku) -> float:
    """Compute a match score in [0.0, 1.0] between a recall notice dict and a Sku."""
    r_gtins = [g.zfill(14) for g in recall.get("gtins", [])]
    if sku.gtin.zfill(14) in r_gtins:
        return 1.0
    title = str(recall.get("title", ""))
    if sku.name and sku.name.lower() in title.lower():
        return 0.75
    return 0.0


def match_recall_to_skus(recall: dict, skus: list[Sku]) -> list[Sku]:
    """Return all Skus matched by a recall dict (by GTIN first, then product name)."""
    matched: list[Sku] = []
    seen: set[str] = set()
    for g in recall.get("gtins", []):
        for s in match_by_gtin(g, skus):
            if s.sku_id not in seen:
                seen.add(s.sku_id)
                matched.append(s)
    if not matched and recall.get("title"):
        for s in match_by_name(str(recall["title"]), skus):
            if s.sku_id not in seen:
                seen.add(s.sku_id)
                matched.append(s)
    return matched


def best_match(recall: dict, skus: list[Sku]) -> Sku | None:
    """Return the highest-scoring Sku for recall, or None."""
    scored = [(match_score(recall, s), s) for s in skus]
    scored = [pair for pair in scored if pair[0] > 0.0]
    if not scored:
        return None
    scored.sort(key=lambda x: (-x[0], x[1].sku_id))
    return scored[0][1]


def unmatched_recalls(recalls: list[dict], skus: list[Sku]) -> list[dict]:
    """Return recall notices that do not match any Sku in skus."""
    return [r for r in recalls if not match_recall_to_skus(r, skus)]


def match_report(recalls: list[dict], skus: list[Sku]) -> dict:
    """Summarize recall-to-SKU matching results."""
    unmatched = unmatched_recalls(recalls, skus)
    return {
        "total_recalls": len(recalls),
        "matched_recalls": len(recalls) - len(unmatched),
        "unmatched_recalls": len(unmatched),
    }
