"""Match external recall notices to catalog SKUs by GTIN, lot code, and product name."""
from __future__ import annotations

from dataclasses import dataclass
from contract import Sku
from recallstorm.gs1.gtin import normalize_gtin
from recallstorm.gs1.lots import lot_matches_recall


@dataclass(frozen=True)
class GtinIndex:
    """Fast lookup index from normalized 14-digit GTIN to list of SKUs."""

    by_gtin: dict[str, tuple[Sku, ...]]

    @classmethod
    def build(cls, skus: list[Sku]) -> GtinIndex:
        mapping: dict[str, list[Sku]] = {}
        for s in skus:
            g = normalize_gtin(s.gtin)
            mapping.setdefault(g, []).append(s)
        return cls(by_gtin={k: tuple(v) for k, v in mapping.items()})


def match_by_gtin(gtin: str, skus: list[Sku]) -> list[Sku]:
    """Return all SKUs matching the normalized 14-digit GTIN."""
    target = normalize_gtin(gtin)
    return [s for s in skus if normalize_gtin(s.gtin) == target]


def match_by_lot(lot: str, lot_map: dict[str, list[str]], skus: list[Sku]) -> list[Sku]:
    """Return all SKUs whose lots in lot_map (sku_id -> list[lot]) match lot."""
    matched_ids = {sku_id for sku_id, lots in lot_map.items() if lot_matches_recall(lot, lots)}
    return [s for s in skus if s.sku_id in matched_ids]


def match_by_name(query: str, skus: list[Sku], threshold: float = 0.5) -> list[Sku]:
    """Fuzzy token-overlap match of query against SKU brand + name."""
    if not isinstance(query, str) or not query.strip():
        return []
    q_tokens = {t.lower() for t in query.split() if len(t) > 2}
    if not q_tokens:
        return []
    out: list[Sku] = []
    for s in skus:
        s_tokens = {t.lower().strip(",.") for t in (s.brand + " " + s.name).split() if len(t) > 2}
        if not s_tokens:
            continue
        overlap = len(q_tokens & s_tokens) / max(1, min(len(q_tokens), len(s_tokens)))
        if overlap >= threshold:
            out.append(s)
    return out


def match_score(recall: dict, sku: Sku) -> float:
    """Compute a similarity score in [0.0, 1.0] between a recall dict and a Sku."""
    gtins = [normalize_gtin(g) for g in recall.get("gtins", []) if str(g).strip()]
    if normalize_gtin(sku.gtin) in gtins:
        return 1.0
    title = str(recall.get("title") or recall.get("product_description") or "")
    q_tokens = {t.lower().strip(",.") for t in title.split() if len(t) > 2}
    s_tokens = {t.lower().strip(",.") for t in (sku.brand + " " + sku.name).split() if len(t) > 2}
    if not q_tokens or not s_tokens:
        return 0.0
    return round(len(q_tokens & s_tokens) / max(1, len(s_tokens)), 3)


def match_recall_to_skus(recall: dict, skus: list[Sku]) -> list[Sku]:
    """Match a recall dictionary to catalog SKUs by exact GTIN first, then high-confidence name match."""
    hits: list[Sku] = []
    seen: set[str] = set()
    for g in recall.get("gtins", []):
        for s in match_by_gtin(g, skus):
            if s.sku_id not in seen:
                seen.add(s.sku_id)
                hits.append(s)
    if hits:
        return hits
    title = str(recall.get("title") or recall.get("product_description") or "")
    for s in match_by_name(title, skus, threshold=0.6):
        if s.sku_id not in seen:
            seen.add(s.sku_id)
            hits.append(s)
    return hits


def best_match(recall: dict, skus: list[Sku]) -> Sku | None:
    """Return the single highest-scoring Sku for a recall, or None if score < 0.5."""
    if not skus:
        return None
    scored = sorted(((match_score(recall, s), s) for s in skus), key=lambda x: (-x[0], x[1].sku_id))
    return scored[0][1] if scored[0][0] >= 0.5 else None


def unmatched_recalls(recalls: list[dict], skus: list[Sku]) -> list[dict]:
    """Return recalls that did not match any catalog SKU."""
    return [r for r in recalls if not match_recall_to_skus(r, skus)]


def match_report(recalls: list[dict], skus: list[Sku]) -> dict:
    """Generate a summary report of recall-to-SKU matching."""
    matched = sum(1 for r in recalls if match_recall_to_skus(r, skus))
    return {
        "total_recalls": len(recalls),
        "matched_recalls": matched,
        "unmatched_recalls": len(recalls) - matched,
    }
