"""Configuration management for Recall Storm runs and scenarios."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from recallstorm.core.errors import ScenarioError


@dataclass(frozen=True)
class Config:
    """Platform and scenario configuration."""

    scenario_id: str = "ca_red3"
    state: str = "CA"
    rule_ids: tuple[str, ...] = ("CA_AB418_RED3",)
    as_of: str = "2026-12-30T18:00:00-08:00"
    deadline: str = "2027-01-01T00:00:00-08:00"
    data_dir: str = "data"
    out_dir: str = "out/default"
    generator: str = "recallstorm/1.0"
    extra: dict[str, str] = field(default_factory=dict)


def default_config() -> Config:
    """Return the default configuration."""
    return Config()


def get_scenario_path(data_dir: str | Path, scenario_id: str) -> str:
    """Return the path to data/scenario_<id>.json."""
    if not isinstance(scenario_id, str) or not scenario_id.strip():
        raise ScenarioError("scenario_id must be a non-empty string")
    scen = scenario_id.strip()
    base = Path(data_dir)
    if scen.endswith(".json") and Path(scen).exists():
        return str(Path(scen))
    return str(base / f"scenario_{scen}.json")


def load_config(path: str | Path) -> Config:
    """Load a Config from a scenario JSON file."""
    p = Path(path)
    if not p.exists():
        raise ScenarioError(f"Scenario file not found: {p}")
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ScenarioError(f"Failed to parse scenario JSON: {p}") from exc
    if not isinstance(raw, dict):
        raise ScenarioError("Scenario JSON must be an object")
    cfg = Config(
        scenario_id=str(raw.get("scenario_id", "ca_red3")),
        state=str(raw.get("state", "CA")),
        rule_ids=tuple(str(r) for r in raw.get("rule_ids", ["CA_AB418_RED3"])),
        as_of=str(raw.get("as_of", "2026-12-30T18:00:00-08:00")),
        deadline=str(raw.get("deadline", "2027-01-01T00:00:00-08:00")),
        data_dir=str(raw.get("data_dir", str(p.parent))),
        out_dir=str(raw.get("out_dir", "out/default")),
        generator=str(raw.get("generator", "recallstorm/1.0")),
        extra={k: str(v) for k, v in raw.items() if k not in {
            "scenario_id", "state", "rule_ids", "as_of", "deadline", "data_dir", "out_dir", "generator"
        }},
    )
    issues = validate_config(cfg)
    if issues:
        raise ScenarioError(f"Invalid config: {'; '.join(issues)}")
    return cfg


def merge_overrides(cfg: Config, overrides: dict) -> Config:
    """Return a new Config with overrides merged in."""
    if not isinstance(cfg, Config):
        raise TypeError("cfg must be a Config")
    if not isinstance(overrides, dict):
        raise TypeError("overrides must be a dict")
    d = config_to_dict(cfg)
    for k, v in overrides.items():
        if v is not None:
            d[k] = v
    rule_ids = d.get("rule_ids", cfg.rule_ids)
    if isinstance(rule_ids, list):
        rule_ids = tuple(str(x) for x in rule_ids)
    return Config(
        scenario_id=str(d["scenario_id"]),
        state=str(d["state"]),
        rule_ids=tuple(rule_ids),
        as_of=str(d["as_of"]),
        deadline=str(d["deadline"]),
        data_dir=str(d["data_dir"]),
        out_dir=str(d["out_dir"]),
        generator=str(d["generator"]),
        extra=dict(d.get("extra", {})),
    )


def validate_config(cfg: Config) -> list[str]:
    """Validate configuration fields and return a list of error strings."""
    if not isinstance(cfg, Config):
        return ["cfg is not a Config instance"]
    issues: list[str] = []
    if not cfg.scenario_id.strip():
        issues.append("scenario_id is empty")
    if not cfg.state.strip() or len(cfg.state.strip()) != 2:
        issues.append("state must be a 2-letter code")
    if not cfg.rule_ids:
        issues.append("rule_ids cannot be empty")
    try:
        as_of_dt = datetime.fromisoformat(cfg.as_of)
    except ValueError:
        issues.append(f"invalid as_of datetime: {cfg.as_of}")
        as_of_dt = None
    try:
        dl_dt = datetime.fromisoformat(cfg.deadline)
    except ValueError:
        issues.append(f"invalid deadline datetime: {cfg.deadline}")
        dl_dt = None
    if as_of_dt and dl_dt and as_of_dt >= dl_dt:
        issues.append("as_of must be strictly before deadline")
    return issues


def config_from_env(prefix: str = "RECALLSTORM_", env: dict[str, str] | None = None) -> Config:
    """Build a Config from environment variables."""
    source = env if env is not None else os.environ
    base = default_config()
    overrides: dict = {}
    if f"{prefix}SCENARIO_ID" in source:
        overrides["scenario_id"] = source[f"{prefix}SCENARIO_ID"]
    if f"{prefix}STATE" in source:
        overrides["state"] = source[f"{prefix}STATE"]
    if f"{prefix}DATA_DIR" in source:
        overrides["data_dir"] = source[f"{prefix}DATA_DIR"]
    if f"{prefix}OUT_DIR" in source:
        overrides["out_dir"] = source[f"{prefix}OUT_DIR"]
    if f"{prefix}RULE_IDS" in source:
        overrides["rule_ids"] = tuple(x.strip() for x in source[f"{prefix}RULE_IDS"].split(",") if x.strip())
    return merge_overrides(base, overrides)


def config_to_dict(cfg: Config) -> dict:
    """Convert Config to a plain dictionary."""
    if not isinstance(cfg, Config):
        raise TypeError("cfg must be a Config")
    return {
        "scenario_id": cfg.scenario_id,
        "state": cfg.state,
        "rule_ids": list(cfg.rule_ids),
        "as_of": cfg.as_of,
        "deadline": cfg.deadline,
        "data_dir": cfg.data_dir,
        "out_dir": cfg.out_dir,
        "generator": cfg.generator,
        "extra": dict(cfg.extra),
    }


def get_deadline(cfg: Config) -> datetime:
    """Parse and return the scenario deadline datetime."""
    if not isinstance(cfg, Config):
        raise TypeError("cfg must be a Config")
    try:
        return datetime.fromisoformat(cfg.deadline)
    except ValueError as exc:
        raise ScenarioError(f"Invalid deadline in config: {cfg.deadline}") from exc
