"""Property tests for recallstorm.core.registry."""
from recallstorm.core.registry import list_modules, register_module, reset_registry, src_path_for


def test_registry_determinism():
    reset_registry()
    for i in range(20):
        name = f"recallstorm.mod_{i:02d}"
        path = f"recallstorm/mod_{i:02d}.py"
        register_module(name, path)
        assert src_path_for(name) == path
    mods = list_modules()
    assert mods == sorted(mods)
    assert len(mods) == 20
