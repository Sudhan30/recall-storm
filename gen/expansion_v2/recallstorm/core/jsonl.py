"""JSONL reading, writing, schema validation, and deterministic serialization."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator

from contract import PLAN_TYPES
from recallstorm.core.errors import DataValidationError


def stable_dumps(obj: dict) -> str:
    """Serialize a dictionary to a deterministic single-line JSON string."""
    if not isinstance(obj, dict):
        raise TypeError("obj must be a dict")
    return json.dumps(obj, sort_keys=False, ensure_ascii=False, separators=(",", ":"))


def read_jsonl(path: str) -> list[dict]:
    """Read all JSONL lines from path into a list of dictionaries."""
    return list(iter_jsonl(path))


def iter_jsonl(path: str) -> Iterator[dict]:
    """Yield parsed JSON objects line-by-line from a JSONL file."""
    p = Path(path)
    if not p.exists():
        raise DataValidationError(f"JSONL file not found: {path}")
    with p.open("r", encoding="utf-8") as fh:
        for idx, line in enumerate(fh, 1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                obj = json.loads(stripped)
            except Exception as exc:
                raise DataValidationError(f"Invalid JSON at {path}:{idx}: {exc}") from exc
            if not isinstance(obj, dict):
                raise DataValidationError(f"Non-object JSON at {path}:{idx}")
            yield obj


def write_jsonl(path: str, records: list[dict]) -> int:
    """Write a list of dictionaries to a JSONL file and return the record count."""
    if not isinstance(records, list):
        raise TypeError("records must be a list")
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with p.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(stable_dumps(rec) + "\n")
            count += 1
    return count


def append_jsonl(path: str, record: dict) -> None:
    """Append a single dictionary record to a JSONL file."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(stable_dumps(record) + "\n")


def validate_record(rec: dict, record_type: str | None = None) -> list[str]:
    """Validate a plan.jsonl record against PLAN_TYPES required fields."""
    if not isinstance(rec, dict):
        return ["Record is not a dictionary"]
    rtype = record_type or rec.get("type")
    if not rtype or rtype not in PLAN_TYPES:
        return [f"Unknown or missing record type: {rtype!r}"]
    issues: list[str] = []
    for req_field in PLAN_TYPES[rtype]:
        if req_field not in rec:
            issues.append(f"Missing required field {req_field!r} for type {rtype!r}")
    if "src" in rec and (not isinstance(rec["src"], str) or not rec["src"].strip()):
        issues.append("Field 'src' must be a non-empty string")
    return issues


def record_with_src(rec: dict, src: str) -> dict:
    """Return a copy of rec with the 'src' provenance field set."""
    if not isinstance(rec, dict):
        raise TypeError("rec must be a dict")
    if not isinstance(src, str) or not src.strip():
        raise ValueError("src must be a non-empty string")
    out = dict(rec)
    out["src"] = src
    return out


def sort_records(records: list[dict], key_fields: tuple[str, ...] = ("type",)) -> list[dict]:
    """Deterministically sort a list of dictionary records by key_fields."""
    return sorted(records, key=lambda r: tuple(str(r.get(k, "")) for k in key_fields))


def dedupe_by_key(records: list[dict], key_field: str) -> list[dict]:
    """Deduplicate records preserving first-seen order by key_field."""
    seen: set = set()
    out: list[dict] = []
    for rec in records:
        val = rec.get(key_field)
        if val not in seen:
            seen.add(val)
            out.append(rec)
    return out
