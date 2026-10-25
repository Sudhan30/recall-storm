"""Parse FSIS and FDA RSS recall feeds into normalized recall records."""
from __future__ import annotations

import hashlib
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime
from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class RecallFeed:
    """Container for normalized recall feed items."""

    source: str
    items: tuple[dict, ...] = field(default_factory=tuple)


def parse_fsis_recall(raw: dict) -> dict:
    """Parse an FSIS recall JSON object into a normalized recall dictionary."""
    if not isinstance(raw, dict) or not raw.get("recall_number"):
        raise DataValidationError("FSIS recall requires a non-empty recall_number")
    states_raw = raw.get("states", "US")
    if isinstance(states_raw, str):
        states = [s.strip().upper() for s in states_raw.split(",") if s.strip()]
    elif isinstance(states_raw, list):
        states = [str(s).strip().upper() for s in states_raw]
    else:
        states = ["US"]
    return {
        "recall_id": str(raw["recall_number"]).strip(),
        "source": "FSIS",
        "title": str(raw.get("title", "")).strip(),
        "date": str(raw.get("recall_date", "2026-01-01")).strip(),
        "states": states or ["US"],
        "reason": str(raw.get("summary", "")).strip(),
    }


def feed_item_to_recall(item: dict) -> dict:
    """Convert a generic RSS/Atom feed item dictionary into a normalized recall."""
    if not isinstance(item, dict) or not item.get("id"):
        raise DataValidationError("Feed item requires 'id'")
    states = item.get("states", ["US"])
    if isinstance(states, str):
        states = [s.strip().upper() for s in states.split(",") if s.strip()]
    return {
        "recall_id": str(item["id"]).strip(),
        "source": str(item.get("source", "FDA_RSS")).strip(),
        "title": str(item.get("title", "")).strip(),
        "date": str(item.get("date", "2026-01-01")).strip(),
        "states": list(states) if states else ["US"],
        "reason": str(item.get("description", "")).strip(),
    }


def parse_fda_rss(xml_or_dict: str | dict) -> list[dict]:
    """Parse an FDA RSS XML string or pre-parsed dict into normalized recall records."""
    if isinstance(xml_or_dict, dict):
        items = xml_or_dict.get("items", [])
        return [feed_item_to_recall(it) for it in items]
    if not isinstance(xml_or_dict, str) or not xml_or_dict.strip():
        raise DataValidationError("Empty XML string for FDA RSS")
    try:
        root = ET.fromstring(xml_or_dict)
    except ET.ParseError as exc:
        raise DataValidationError("Invalid RSS XML") from exc
    out: list[dict] = []
    for idx, item_el in enumerate(root.findall(".//item")):
        guid = item_el.findtext("guid") or f"FDA-RSS-{idx}"
        title = item_el.findtext("title") or ""
        pub_date = item_el.findtext("pubDate") or "2026-01-01"
        desc = item_el.findtext("description") or ""
        out.append(
            feed_item_to_recall(
                {"id": guid, "source": "FDA_RSS", "title": title, "date": pub_date, "description": desc}
            )
        )
    return out


def dedupe_recalls(recalls: list[dict]) -> list[dict]:
    """Deduplicate recalls by recall_id while preserving order."""
    seen: set[str] = set()
    out: list[dict] = []
    for r in recalls:
        rid = r.get("recall_id")
        if rid and rid not in seen:
            seen.add(rid)
            out.append(r)
    return out


def recall_since(recalls: list[dict], since_dt: datetime | str) -> list[dict]:
    """Filter recalls whose date is >= since_dt."""
    cutoff = since_dt.strftime("%Y-%m-%d") if isinstance(since_dt, datetime) else str(since_dt)[:10]
    return [r for r in recalls if str(r.get("date", ""))[:10] >= cutoff]


def recall_by_state(recalls: list[dict], state: str) -> list[dict]:
    """Filter recalls applicable to a 2-letter state code or nationwide ('US')."""
    if not isinstance(state, str) or len(state.strip()) != 2:
        raise DataValidationError("state must be a 2-letter code")
    st = state.strip().upper()
    return [r for r in recalls if st in r.get("states", []) or "US" in r.get("states", [])]


def merge_recall_sources(*sources: list[dict]) -> list[dict]:
    """Merge and deduplicate multiple lists of recall records sorted by recall_id."""
    combined: list[dict] = []
    for src in sources:
        combined.extend(src)
    deduped = dedupe_recalls(combined)
    return sorted(deduped, key=lambda r: str(r.get("recall_id", "")))


def feed_cursor(recalls: list[dict]) -> str:
    """Compute a deterministic cursor hash over a recall list."""
    ids = "|".join(sorted(str(r.get("recall_id", "")) for r in recalls))
    return hashlib.sha256(ids.encode("utf-8")).hexdigest()[:12]
