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


def test_read_write_append(tmp_path):
    p = tmp_path / "test.jsonl"
    recs = [{"id": "B", "v": 2}, {"id": "A", "v": 1}]
    assert write_jsonl(p, recs) == 2
    append_jsonl(p, {"id": "A", "v": 3})
    loaded = read_jsonl(p)
    assert len(loaded) == 3
    assert list(iter_jsonl(p)) == loaded
    deduped = dedupe_by_key(loaded, "id")
    assert len(deduped) == 2
    sorted_recs = sort_records(deduped, ["id"])
    assert [r["id"] for r in sorted_recs] == ["A", "B"]
    assert isinstance(stable_dumps(recs[0]), str)


def test_record_with_src_and_validate():
    raw = {
        "run_id": "RUN-1",
        "scenario_id": "ca_red3",
        "generator": "gen",
        "as_of": "2026-12-30T18:00:00-08:00",
        "rule_ids": ["CA_AB418_RED3"],
    }
    rec = record_with_src(raw, "run", "recallstorm/plan/assemble.py")
    assert validate_record(rec) == []
