"""Module registry and provenance tracking for emitted records."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Registry:
    """In-memory registry of Recall Storm modules and source paths."""

    modules: dict[str, dict] = field(default_factory=dict)


_GLOBAL_REGISTRY = Registry()


def register_module(name: str, src_path: str, version: str = "1.0.0") -> dict:
    """Register a module with its repo-relative src_path and version."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Module name must be a non-empty string")
    if not isinstance(src_path, str) or not src_path.strip():
        raise ValueError("src_path must be a non-empty string")
    entry = {"name": name.strip(), "src": src_path.strip(), "version": str(version)}
    _GLOBAL_REGISTRY.modules[entry["name"]] = entry
    return entry


def get_module(name: str) -> dict | None:
    """Retrieve a registered module entry by name, or None."""
    return _GLOBAL_REGISTRY.modules.get(name)


def list_modules() -> list[str]:
    """Return sorted list of registered module names."""
    return sorted(_GLOBAL_REGISTRY.modules.keys())


def src_path_for(name: str) -> str:
    """Return the repo-relative source path for a module name."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Module name must be a non-empty string")
    entry = _GLOBAL_REGISTRY.modules.get(name)
    if entry:
        return entry["src"]
    if name.endswith(".py"):
        return name
    return name.replace(".", "/") + ".py"


def emit_with_src(record: dict, module_name: str) -> dict:
    """Attach the repo-relative 'src' path for module_name to a record."""
    if not isinstance(record, dict):
        raise TypeError("record must be a dict")
    out = dict(record)
    out["src"] = src_path_for(module_name)
    return out


def module_version(name: str) -> str:
    """Return the version string for a module."""
    entry = _GLOBAL_REGISTRY.modules.get(name)
    return entry["version"] if entry else "1.0.0"


def registry_snapshot() -> dict:
    """Return a copy of all registered modules."""
    return {k: dict(v) for k, v in _GLOBAL_REGISTRY.modules.items()}


def reset_registry() -> None:
    """Clear the global module registry."""
    _GLOBAL_REGISTRY.modules.clear()
