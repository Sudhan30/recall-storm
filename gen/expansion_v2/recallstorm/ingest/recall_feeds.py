"""Parse and merge FSIS and FDA recall feeds."""
from __future__ import annotations

from dataclasses import dataclass, field
import xml.etree.ElementTree as ET

from recallstorm.core.errors import DataValidationError


@dataclass
class RecallFeed:
    """Container for normalized recall feed items."""

    source: str
    items: list[dict] = field(default_factory=list)


def parse_fsis_recall(payload: dict) -> dict:
    """Normalize a USDA FSIS recall dictionary."""
    if not isinstance(payload, dict) or not payload.get("recall_number"):
        raise DataValidationError("Invalid FSIS recall payload: missing recall_number")
    states = payload.get("states") or ["US"]
    if isinstance(states, str):
        states = [s.strip() for s in states.split(",") if s.strip()]
    return {
        "recall_id": str(payload["recall_number"]).strip(),
        "source": "FSIS",
        "title": str(payload.get("title", "")).strip(),
        "date": str(payload.get("recall_date", "2026-01-01")).strip(),
        "states": list(states),
        "reason": str(payload.get("reason", "Contamination")).strip(),
    }


def parse_fda_rss(xml_or_dict: str | dict) -> list[dict]:
    """Parse FDA recall RSS XML or structured dictionary into recall items."""
    if isinstance(xml_or_dict, dict):
        raw_items = xml_or_dict.get("items", [])
        return [feed_item_to_recall(it) for it in raw_items]
    if not isinstance(xml_or_dict, str) or not xml_or_dict.strip():
        raise DataValidationError("Empty FDA RSS XML input")
    try:
        root = ET.fromstring(xml_or_dict)
    except Exception as exc:
        raise DataValidationError(f"Malformed RSS XML: {exc}") from exc
    out: list[dict] = []
    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        guid = (item.findtext("guid") or title or "FDA-000").strip()
        pub_date = (item.findtext("pubDate") or "2026-01-01").strip()
        desc = (item.findtext("description") or "").strip()
        out.append(
            feed_item_to_recall(
                {"recall_id": guid, "title": title, "date": pub_date, "reason": desc, "source": "FDA_RSS"}
            )
        )
    return out


def feed_item_to_recall(item: dict) -> dict:
    """Convert a generic feed item dict into a normalized recall record."""
    if not isinstance(item, dict) or not item.get("recall_id"):
        raise DataValidationError("Feed item missing recall_id")
    return {
        "recall_id": str(item["recall_id"]).strip(),
        "source": str(item.get("source", "FDA")).strip(),
        "title": str(item.get("title", "")).strip(),
        "date": str(item.get("date", "2026-01-01")).strip(),
        "states": list(item.get("states", ["US"])),
        "reason": str(item.get("reason", "")).strip(),
    }


def dedupe_recalls(recalls: list[dict]) -> list[dict]:
    """Deduplicate recall records by recall_id."""
    seen: set[str] = set()
    out: list[dict] = []
    for r in recalls:
        rid = r.get("recall_id")
        if rid and rid not in seen:
            seen.add(rid)
            out.append(r)
    return out


def recall_since(recalls: list[dict], since_iso: str) -> list[dict]:
    """Filter recalls with date >= since_iso."""
    return [r for r in recalls if str(r.get("date", "")) >= since_iso]


def recall_by_state(recalls: list[dict], state: str) -> list[dict]:
    """Filter recalls applicable to state or US nationwide."""
    st = state.upper().strip()
    return [r for r in recalls if st in r.get("states", []) or "US" in r.get("states", [])]


def merge_recall_sources(*sources: list[dict]) -> list[dict]:
    """Merge and deduplicate multiple recall lists sorted by recall_id."""
    combined: list[dict] = []
    for src in sources:
        combined.extend(src)
    deduped = dedupe_recalls(combined)
    return sorted(deduped, key=lambda x: str(x.get("recall_id", "")))


def feed_cursor(recalls: list[dict]) -> str:
    """Return the latest date string in recalls as a pagination cursor."""
    if not recalls:
        return ""
    return max(str(r.get("date", "")) for r in recalls)
