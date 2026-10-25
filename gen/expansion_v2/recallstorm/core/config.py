"""Configuration loading, validation, and environment resolution."""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, replace
from pathlib import Path

from recallstorm.core.errors import ScenarioError


@dataclass(frozen=True)
class Config:
    """Platform configuration parameters."""

    scenario_id: str = "ca_red3"
    state: str = "CA"
    data_dir: str = "data"
    out_dir: str = "out/default"
    as_of: str = "2026-12-30T18:00:00-08:00"
    deadline: str = "2027-01-01T00:00:00-08:00"
    rule_ids: tuple[str, ...] = ("CA_AB418_RED3",)
    seed: int = 42
    log_level: str = "INFO"


def default_config() -> Config:
    """Return the default Recall Storm configuration."""
    return Config()


def get_scenario_path(data_dir: str, scenario_id: str) -> str:
    """Return the path to data/scenario_<id>.json."""
    if not isinstance(data_dir, str) or not data_dir.strip():
        raise ScenarioError("data_dir must be a non-empty string")
    if not isinstance(scenario_id, str) or not scenario_id.strip():
        raise ScenarioError("scenario_id must be a non-empty string")
    fname = scenario_id if scenario_id.startswith("scenario_") else f"scenario_{scenario_id}"
    if not fname.endswith(".json"):
        fname = f"{fname}.json"
    return str(Path(data_dir) / fname)


def load_config(path: str | None = None) -> Config:
    """Load configuration from a JSON file or return defaults when path is None."""
    base = default_config()
    if path is None:
        return base
    p = Path(path)
    if not p.exists():
        raise ScenarioError(f"Configuration file not found: {path}")
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ScenarioError(f"Failed to parse JSON config at {path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise ScenarioError("Config JSON root must be an object")
    return merge_overrides(base, raw)


def merge_overrides(cfg: Config, overrides: dict) -> Config:
    """Merge dictionary overrides into an existing Config instance."""
    if not isinstance(cfg, Config):
        raise TypeError("cfg must be a Config instance")
    if not isinstance(overrides, dict):
        raise TypeError("overrides must be a dict")
    valid_keys = {f.name for f in cfg.__dataclass_fields__.values()}
    filtered: dict = {}
    for k, v in overrides.items():
        if k in valid_keys and v is not None:
            if k == "rule_ids":
                filtered[k] = tuple(str(x) for x in v)
            elif k == "seed":
                filtered[k] = int(v)
            else:
                filtered[k] = str(v)
    return replace(cfg, **filtered)


def validate_config(cfg: Config) -> list[str]:
    """Validate a Config object and return a list of issue strings."""
    if not isinstance(cfg, Config):
        return ["cfg is not a Config instance"]
    issues: list[str] = []
    if not cfg.scenario_id.strip():
        issues.append("scenario_id cannot be empty")
    if not cfg.state.strip():
        issues.append("state cannot be empty")
    if not cfg.data_dir.strip():
        issues.append("data_dir cannot be empty")
    if not cfg.out_dir.strip():
        issues.append("out_dir cannot be empty")
    if not cfg.deadline.strip():
        issues.append("deadline cannot be empty")
    if not cfg.rule_ids:
        issues.append("rule_ids cannot be empty")
    return issues


def config_from_env(prefix: str = "RECALLSTORM_") -> Config:
    """Build a Config by reading environment variables starting with prefix."""
    overrides: dict = {}
    mapping = {
        f"{prefix}SCENARIO_ID": "scenario_id",
        f"{prefix}STATE": "state",
        f"{prefix}DATA_DIR": "data_dir",
        f"{prefix}OUT_DIR": "out_dir",
        f"{prefix}AS_OF": "as_of",
        f"{prefix}DEADLINE": "deadline",
        f"{prefix}SEED": "seed",
        f"{prefix}LOG_LEVEL": "log_level",
    }
    for env_key, field_name in mapping.items():
        if env_key in os.environ:
            overrides[field_name] = os.environ[env_key]
    return merge_overrides(default_config(), overrides)


def config_to_dict(cfg: Config) -> dict:
    """Serialize a Config instance to a plain dictionary."""
    if not isinstance(cfg, Config):
        raise TypeError("cfg must be a Config instance")
    d = asdict(cfg)
    d["rule_ids"] = list(cfg.rule_ids)
    return d


def get_deadline(cfg: Config) -> str:
    """Return the ISO deadline string from a Config."""
    if not isinstance(cfg, Config) or not cfg.deadline.strip():
        raise ScenarioError("Invalid deadline in Config")
    return cfg.deadline
