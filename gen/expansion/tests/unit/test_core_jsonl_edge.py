"""Edge tests for recallstorm.core.jsonl."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.core.jsonl import (
    dedupe_by_key,
    read_jsonl,
    record_with_src,
    validate_record,
    write_jsonl,
)


def test_missing_or_corrupt_jsonl(tmp_path):
    with pytest.raises(DataValidationError):
        read_jsonl(tmp_path / "nope.jsonl")
    bad = tmp_path / "bad.jsonl"
    bad.write_text("not json\n", encoding="utf-8")
    with pytest.raises(DataValidationError):
        read_jsonl(bad)


def test_invalid_record_validation(tmp_path):
    assert validate_record({"type": "unknown"}) != []
    with pytest.raises(DataValidationError):
        record_with_src({"run_id": "1"}, "run", "src.py")
    with pytest.raises(DataValidationError):
        write_jsonl(tmp_path / "x.jsonl", ["not_dict"])  # type: ignore[list-item]
    with pytest.raises(ValueError):
        dedupe_by_key([], "")
