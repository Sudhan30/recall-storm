"""Unit tests for recallstorm.core.jsonl."""
from recallstorm.core.jsonl import (
    append_jsonl,
    dedupe_by_key,
    iter_jsonl,
    read_jsonl,
    record_with_src,
    sort_records,
    stable_dumps,
    validate_record,
    write_jsonl,
)


def test_jsonl_read_write_validate(tmp_path):
    p = tmp_path / "test.jsonl"
    r1 = {
        "type": "run",
        "run_id": "RUN-1",
        "scenario_id": "ca_red3",
        "generator": "recallstorm",
        "as_of": "2026-12-30T18:00:00-08:00",
        "rule_ids": ["CA_AB418_RED3"],
    }
    r1 = record_with_src(r1, "recallstorm/plan/assemble.py")
    assert validate_record(r1) == []
    assert write_jsonl(str(p), [r1]) == 1
    append_jsonl(str(p), r1)
    loaded = read_jsonl(str(p))
    assert len(loaded) == 2
    assert len(list(iter_jsonl(str(p)))) == 2
    deduped = dedupe_by_key(loaded, "run_id")
    assert len(deduped) == 1
    assert len(sort_records(loaded, ("run_id",))) == 2
    assert isinstance(stable_dumps(r1), str)
