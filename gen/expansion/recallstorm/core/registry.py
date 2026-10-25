"""Module provenance registry for tracking record emitter sources."""
from __future__ import annotations

from dataclasses import dataclass, field
from recallstorm.core.errors import DataValidationError
from recallstorm.core.jsonl import record_with_src


@dataclass
class Registry:
    """In-memory registry of Recall Storm modules and their repo-relative paths."""

    modules: dict[str, dict[str, str]] = field(default_factory=dict)


_GLOBAL_REGISTRY = Registry()


def register_module(name: str, src_path: str, version: str = "1.0.0") -> None:
    """Register a module name with its repo-relative src_path and version."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("module name must be a non-empty string")
    if not isinstance(src_path, str) or not src_path.strip():
        raise ValueError("src_path must be a non-empty string")
    if not isinstance(version, str) or not version.strip():
        raise ValueError("version must be a non-empty string")
    _GLOBAL_REGISTRY.modules[name.strip()] = {
        "name": name.strip(),
        "src": src_path.strip(),
        "version": version.strip(),
    }


def get_module(name: str) -> dict[str, str]:
    """Retrieve a registered module entry."""
    if name not in _GLOBAL_REGISTRY.modules:
        raise DataValidationError(f"Module not registered: {name}")
    return dict(_GLOBAL_REGISTRY.modules[name])


def list_modules() -> list[str]:
    """Return sorted list of registered module names."""
    return sorted(_GLOBAL_REGISTRY.modules.keys())


def src_path_for(name: str) -> str:
    """Return the repo-relative source path for a registered module."""
    return get_module(name)["src"]


def module_version(name: str) -> str:
    """Return the version string for a registered module."""
    return get_module(name)["version"]


def emit_with_src(record: dict, rec_type: str, module_name: str) -> dict:
    """Attach the registered module's src path to a plan record and validate."""
    src = _GLOBAL_REGISTRY.modules.get(module_name, {}).get("src", module_name)
    return record_with_src(record, rec_type, src)


def registry_snapshot() -> dict[str, dict[str, str]]:
    """Return a copy of all registered modules."""
    return {k: dict(v) for k, v in _GLOBAL_REGISTRY.modules.items()}


def reset_registry() -> None:
    """Clear the global module registry."""
    _GLOBAL_REGISTRY.modules.clear()
