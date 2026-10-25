"""JSONL reading, writing, sorting, and PLAN_TYPES schema validation."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator
from contract import PLAN_TYPES
from recallstorm.core.errors import DataValidationError


def stable_dumps(obj: object) -> str:
    """Serialize an object to a deterministic single-line JSON string."""
    return json.dumps(obj, sort_keys=False, separators=(", ", ": "), ensure_ascii=False)


def iter_jsonl(path: str | Path) -> Iterator[dict]:
    """Yield parsed dictionary records from a JSONL file."""
    p = Path(path)
    if not p.exists():
        raise DataValidationError(f"JSONL file does not exist: {p}")
    with p.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                rec = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise DataValidationError(f"Invalid JSON at {p}:{line_no}") from exc
            if not isinstance(rec, dict):
                raise DataValidationError(f"Expected JSON object at {p}:{line_no}")
            yield rec


def read_jsonl(path: str | Path) -> list[dict]:
    """Read all records from a JSONL file into a list."""
    return list(iter_jsonl(path))


def write_jsonl(path: str | Path, records: list[dict]) -> int:
    """Write a list of dictionary records to a JSONL file and return count written."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with p.open("w", encoding="utf-8") as fh:
        for rec in records:
            if not isinstance(rec, dict):
                raise DataValidationError("All JSONL records must be dicts")
            fh.write(stable_dumps(rec) + "\n")
            count += 1
    return count


def append_jsonl(path: str | Path, record: dict) -> None:
    """Append a single dictionary record to a JSONL file."""
    if not isinstance(record, dict):
        raise DataValidationError("Record must be a dict")
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(stable_dumps(record) + "\n")


def validate_record(rec: dict, rec_type: str | None = None) -> list[str]:
    """Validate a plan.jsonl record against PLAN_TYPES required fields."""
    if not isinstance(rec, dict):
        return ["Record is not a dict"]
    rtype = rec_type or rec.get("type")
    if not isinstance(rtype, str) or rtype not in PLAN_TYPES:
        return [f"Unknown or missing record type: {rtype}"]
    issues: list[str] = []
    for req_field in PLAN_TYPES[rtype]:
        if req_field not in rec:
            issues.append(f"Missing required field '{req_field}' for type '{rtype}'")
    src = rec.get("src")
    if not isinstance(src, str) or not src.strip():
        issues.append(f"Empty or invalid 'src' field for type '{rtype}'")
    return issues


def record_with_src(rec: dict, rec_type: str, src: str) -> dict:
    """Build a validated plan.jsonl record with 'type' and 'src' attached."""
    if not isinstance(rec, dict):
        raise DataValidationError("rec must be a dict")
    out = {"type": rec_type, **rec, "src": src}
    issues = validate_record(out, rec_type)
    if issues:
        raise DataValidationError("; ".join(issues))
    return out


def sort_records(records: list[dict], key_fields: tuple[str, ...] | list[str]) -> list[dict]:
    """Deterministically sort records by the specified key fields."""
    if not isinstance(records, list):
        raise TypeError("records must be a list")
    return sorted(records, key=lambda r: tuple(str(r.get(k, "")) for k in key_fields))


def dedupe_by_key(records: list[dict], key_field: str) -> list[dict]:
    """Deduplicate records preserving first seen order by key_field."""
    if not isinstance(key_field, str) or not key_field:
        raise ValueError("key_field must be a non-empty string")
    seen: set = set()
    out: list[dict] = []
    for rec in records:
        k = rec.get(key_field)
        if k not in seen:
            seen.add(k)
            out.append(rec)
    return out
