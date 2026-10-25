"""Unit tests for recallstorm.core.registry."""
from recallstorm.core.registry import (
    Registry,
    emit_with_src,
    get_module,
    list_modules,
    module_version,
    register_module,
    registry_snapshot,
    reset_registry,
    src_path_for,
)


def test_registry_lifecycle():
    reset_registry()
    reg = Registry()
    assert reg.modules == {}
    register_module("rules.engine", "recallstorm/rules/engine.py", "1.2.0")
    assert list_modules() == ["rules.engine"]
    assert src_path_for("rules.engine") == "recallstorm/rules/engine.py"
    assert module_version("rules.engine") == "1.2.0"
    assert get_module("rules.engine")["src"] == "recallstorm/rules/engine.py"
    snap = registry_snapshot()
    assert "rules.engine" in snap

    rec = emit_with_src(
        {
            "run_id": "RUN-1",
            "scenario_id": "ca_red3",
            "generator": "g",
            "as_of": "2026-12-30T18:00:00-08:00",
            "rule_ids": ["CA_AB418_RED3"],
        },
        "run",
        "rules.engine",
    )
    assert rec["src"] == "recallstorm/rules/engine.py"
