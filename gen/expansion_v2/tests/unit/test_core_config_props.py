"""Property tests for recallstorm.core.config."""
import random
from recallstorm.core.config import config_to_dict, default_config, merge_overrides, validate_config


def test_config_merge_props():
    rng = random.Random(42)
    base = default_config()
    for i in range(25):
        seed = rng.randint(1, 10000)
        st = rng.choice(["CA", "NY", "MN", "IL", "WA"])
        cfg = merge_overrides(base, {"seed": seed, "state": st, "scenario_id": f"sc_{i}"})
        assert validate_config(cfg) == []
        d = config_to_dict(cfg)
        assert d["seed"] == seed
        assert d["state"] == st
