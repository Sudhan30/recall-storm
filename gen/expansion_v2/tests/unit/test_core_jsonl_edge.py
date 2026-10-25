"""Edge case tests for recallstorm.core.jsonl."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.core.jsonl import read_jsonl, record_with_src, validate_record


def test_jsonl_invalid(tmp_path):
    with pytest.raises(DataValidationError):
        read_jsonl(str(tmp_path / "nope.jsonl"))
    bad = tmp_path / "bad.jsonl"
    bad.write_text("not json\n", encoding="utf-8")
    with pytest.raises(DataValidationError):
        read_jsonl(str(bad))

    issues = validate_record({"type": "run", "run_id": "1"})
    assert len(issues) > 0
    with pytest.raises(ValueError):
        record_with_src({}, "")
