"""Property tests for recallstorm.core.jsonl."""
import random
from recallstorm.core.jsonl import dedupe_by_key, sort_records, stable_dumps


def test_jsonl_sort_and_dedupe_props():
    rng = random.Random(42)
    recs = [{"id": f"K{rng.randint(1, 10)}", "v": i} for i in range(40)]
    s1 = sort_records(recs, ("id", "v"))
    s2 = sort_records(list(reversed(recs)), ("id", "v"))
    assert s1 == s2
    dd = dedupe_by_key(s1, "id")
    assert len(dd) <= 10
    for r in dd:
        assert stable_dumps(r) == stable_dumps(r)
