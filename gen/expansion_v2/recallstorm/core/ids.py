"""Deterministic ID generation and parsing for Recall Storm records."""
from __future__ import annotations

import hashlib
import re

_CLEAN_RE = re.compile(r"[^A-Za-z0-9_-]+")


def _clean_token(val: str) -> str:
    if not isinstance(val, str) or not val.strip():
        raise ValueError("ID component must be a non-empty string")
    cleaned = _CLEAN_RE.sub("_", val.strip())
    return cleaned.strip("_") or "X"


def _short_hash(*parts: str) -> str:
    joined = "|".join(parts)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:8]


def make_run_id(scenario_id: str, as_of: str = "") -> str:
    """Create a deterministic run ID from scenario_id and optional as_of timestamp."""
    sc = _clean_token(scenario_id)
    digest = _short_hash("RUN", sc, str(as_of or ""))
    return f"RUN-{sc}-{digest}"


def make_task_id(store_id: str, sku_id: str, action: str, seq: int = 0) -> str:
    """Create a deterministic shelf task ID."""
    if not isinstance(seq, int) or seq < 0:
        raise ValueError("seq must be a non-negative integer")
    st = _clean_token(store_id)
    sk = _clean_token(sku_id)
    ac = _clean_token(action)
    return f"TSK-{st}-{sk}-{ac}-{seq:04d}"


def make_evidence_id(sku_id: str, rule_id: str) -> str:
    """Create a deterministic evidence ID for a SKU and Rule."""
    sk = _clean_token(sku_id)
    rl = _clean_token(rule_id)
    return f"EVD-{sk}-{rl}"


def make_alloc_id(dc_id: str, store_id: str, sub_sku_id: str) -> str:
    """Create a deterministic substitute allocation ID."""
    dc = _clean_token(dc_id)
    st = _clean_token(store_id)
    sb = _clean_token(sub_sku_id)
    return f"ALC-{dc}-{st}-{sb}"


def make_manifest_id(truck_id: str, seq: int = 0) -> str:
    """Create a deterministic route manifest ID."""
    if not isinstance(seq, int) or seq < 0:
        raise ValueError("seq must be a non-negative integer")
    tr = _clean_token(truck_id)
    return f"MNF-{tr}-{seq:03d}"


def make_handoff_id(kind: str, from_id: str, to_id: str, seq: int = 0) -> str:
    """Create a deterministic handoff ID."""
    if not isinstance(seq, int) or seq < 0:
        raise ValueError("seq must be a non-negative integer")
    kd = _clean_token(kind)
    fr = _clean_token(from_id)
    to = _clean_token(to_id)
    return f"HND-{kd}-{fr}-{to}-{seq:03d}"


def make_exc_id(store_id: str, note_id: str) -> str:
    """Create a deterministic exception ID from store_id and note_id."""
    st = _clean_token(store_id)
    nt = _clean_token(note_id)
    return f"EXC-{st}-{nt}"


def parse_id(raw_id: str) -> dict:
    """Parse a structured Recall Storm ID into its prefix and parts."""
    if not isinstance(raw_id, str) or "-" not in raw_id:
        raise ValueError(f"Invalid Recall Storm ID: {raw_id!r}")
    parts = raw_id.split("-")
    prefix = parts[0]
    if prefix not in {"RUN", "TSK", "EVD", "ALC", "MNF", "HND", "EXC"}:
        raise ValueError(f"Unrecognized ID prefix: {prefix!r}")
    return {"id": raw_id, "prefix": prefix, "parts": parts[1:]}


def validate_id_prefix(raw_id: str, expected_prefix: str) -> bool:
    """Return True if raw_id is a valid ID starting with expected_prefix."""
    if not isinstance(raw_id, str) or not isinstance(expected_prefix, str):
        return False
    try:
        parsed = parse_id(raw_id)
        return parsed["prefix"] == expected_prefix
    except ValueError:
        return False
