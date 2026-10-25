"""OURS. Repo-relative module path for the `src` field of plan records."""
from __future__ import annotations

import pathlib

_ROOT = pathlib.Path(__file__).resolve().parents[3]


def src_of(file: str) -> str:
    p = pathlib.Path(file).resolve()
    try:
        return p.relative_to(_ROOT).as_posix()
    except ValueError:
        return p.name
