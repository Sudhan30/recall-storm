"""Deterministic ID scheme for Recall Storm records."""
from __future__ import annotations

import hashlib
from datetime import datetime
from contract import Action, ExceptionKind, HandoffKind

VALID_PREFIXES = ("RUN", "TSK", "EVD", "ALC", "MNF", "HND", "EXC")


def _short_hash(payload: str, length: int = 8) -> str:
    """Compute a deterministic short hex digest."""
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:length].upper()


def _require_nonempty(val: str, name: str) -> str:
    if not isinstance(val, str) or not val.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return val.strip()


def make_run_id(scenario_id: str, as_of: datetime | str) -> str:
    """Create a deterministic run ID from scenario_id and as_of timestamp."""
    scen = _require_nonempty(scenario_id, "scenario_id")
    if isinstance(as_of, datetime):
        ts = as_of.isoformat()
    elif isinstance(as_of, str) and as_of.strip():
        ts = as_of.strip()
    else:
        raise ValueError("as_of must be a datetime or non-empty ISO string")
    digest = _short_hash(f"RUN|{scen}|{ts}", 8)
    return f"RUN-{scen}-{digest}"


def make_task_id(store_id: str, sku_id: str, action: Action | str, seq: int) -> str:
    """Create a deterministic shelf task ID."""
    st = _require_nonempty(store_id, "store_id")
    sk = _require_nonempty(sku_id, "sku_id")
    act = action.value if isinstance(action, Action) else _require_nonempty(str(action), "action")
    if act not in {a.value for a in Action}:
        raise ValueError(f"Invalid action: {act}")
    if not isinstance(seq, int) or isinstance(seq, bool) or seq < 0:
        raise ValueError("seq must be a non-negative integer")
    digest = _short_hash(f"TSK|{st}|{sk}|{act}|{seq}", 6)
    return f"TSK-{st}-{sk}-{seq:03d}-{digest}"


def make_evidence_id(sku_id: str, rule_id: str) -> str:
    """Create a deterministic evidence ID for a SKU and rule."""
    sk = _require_nonempty(sku_id, "sku_id")
    rl = _require_nonempty(rule_id, "rule_id")
    digest = _short_hash(f"EVD|{sk}|{rl}", 6)
    return f"EVD-{sk}-{rl}-{digest}"


def make_alloc_id(dc_id: str, sub_sku_id: str, store_id: str) -> str:
    """Create a deterministic substitute allocation ID."""
    dc = _require_nonempty(dc_id, "dc_id")
    sub = _require_nonempty(sub_sku_id, "sub_sku_id")
    st = _require_nonempty(store_id, "store_id")
    digest = _short_hash(f"ALC|{dc}|{sub}|{st}", 6)
    return f"ALC-{dc}-{sub}-{st}-{digest}"


def make_manifest_id(truck_id: str, dc_id: str) -> str:
    """Create a deterministic route manifest ID."""
    tr = _require_nonempty(truck_id, "truck_id")
    dc = _require_nonempty(dc_id, "dc_id")
    digest = _short_hash(f"MNF|{tr}|{dc}", 6)
    return f"MNF-{dc}-{tr}-{digest}"


def make_handoff_id(kind: HandoffKind | str, from_id: str, to_id: str, seq: int = 0) -> str:
    """Create a deterministic handoff ID."""
    k = kind.value if isinstance(kind, HandoffKind) else _require_nonempty(str(kind), "kind")
    if k not in {h.value for h in HandoffKind}:
        raise ValueError(f"Invalid handoff kind: {k}")
    fr = _require_nonempty(from_id, "from_id")
    to = _require_nonempty(to_id, "to_id")
    if not isinstance(seq, int) or isinstance(seq, bool) or seq < 0:
        raise ValueError("seq must be a non-negative integer")
    digest = _short_hash(f"HND|{k}|{fr}|{to}|{seq}", 6)
    return f"HND-{k}-{fr}-{to}-{seq:02d}-{digest}"


def make_exc_id(store_id: str, note_id: str, kind: ExceptionKind | str) -> str:
    """Create a deterministic exception ID."""
    st = _require_nonempty(store_id, "store_id")
    nt = _require_nonempty(note_id, "note_id")
    k = kind.value if isinstance(kind, ExceptionKind) else _require_nonempty(str(kind), "kind")
    if k not in {e.value for e in ExceptionKind}:
        raise ValueError(f"Invalid exception kind: {k}")
    digest = _short_hash(f"EXC|{st}|{nt}|{k}", 6)
    return f"EXC-{st}-{nt}-{digest}"


def parse_id(id_str: str) -> tuple[str, str]:
    """Parse an ID string into (prefix, body)."""
    s = _require_nonempty(id_str, "id_str")
    if "-" not in s:
        raise ValueError(f"Malformed ID without separator: {s}")
    prefix, body = s.split("-", 1)
    if prefix not in VALID_PREFIXES or not body:
        raise ValueError(f"Unrecognized ID prefix or empty body: {s}")
    return prefix, body


def validate_id_prefix(id_str: str, expected_prefix: str) -> bool:
    """Check whether id_str starts with expected_prefix and is well-formed."""
    if not isinstance(id_str, str) or not isinstance(expected_prefix, str):
        return False
    try:
        prefix, _ = parse_id(id_str)
        return prefix == expected_prefix
    except ValueError:
        return False
