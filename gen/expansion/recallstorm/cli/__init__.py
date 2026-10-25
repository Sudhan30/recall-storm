"""CLI package: command-line entry point and subcommands."""
from __future__ import annotations

from recallstorm.cli.main import (
    build_parser,
    cmd_explain,
    cmd_replay,
    cmd_run,
    cmd_scenarios,
    cmd_stats,
    cmd_validate,
    exit_code_for,
    main,
)

__all__ = [
    "main",
    "build_parser",
    "cmd_run",
    "cmd_validate",
    "cmd_stats",
    "cmd_explain",
    "cmd_replay",
    "cmd_scenarios",
    "exit_code_for",
]
