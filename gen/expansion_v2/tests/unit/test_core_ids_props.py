"""Property tests for recallstorm.core.ids."""
import random
from recallstorm.core.ids import (
    make_alloc_id,
    make_evidence_id,
    make_exc_id,
    make_handoff_id,
    make_manifest_id,
    make_run_id,
    make_task_id,
    parse_id,
    validate_id_prefix,
)


def test_id_determinism_and_prefix_props():
    rng = random.Random(42)
    for i in range(40):
        s_id = f"ST{rng.randint(100, 999)}"
        k_id = f"SKU{rng.randint(1000, 9999)}"
        r_id = f"RL{rng.randint(1, 50)}"
        seq = rng.randint(0, 500)

        t1 = make_task_id(s_id, k_id, "PULL", seq)
        t2 = make_task_id(s_id, k_id, "PULL", seq)
        assert t1 == t2
        assert validate_id_prefix(t1, "TSK")
        assert parse_id(t1)["prefix"] == "TSK"

        e1 = make_evidence_id(k_id, r_id)
        assert validate_id_prefix(e1, "EVD")
        assert validate_id_prefix(make_alloc_id("DC1", s_id, k_id), "ALC")
        assert validate_id_prefix(make_manifest_id("TR1", seq), "MNF")
        assert validate_id_prefix(make_handoff_id("FLOATER", "F1", s_id, seq), "HND")
        assert validate_id_prefix(make_exc_id(s_id, f"N{i}"), "EXC")
        assert validate_id_prefix(make_run_id(f"sc_{i}"), "RUN")
