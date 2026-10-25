"""OURS. Hidden acceptance tests (never in any prompt).

Run against one generated tree at a time:
    PYTHONPATH=gen/core pytest acceptance -q --junitxml reports/accept_core.xml
A package the tree does not have (e.g. core has no route) is skipped via pytest.importorskip.
Data comes from data/ (override with RECALLSTORM_DATA=dir).
"""
from __future__ import annotations

import csv
import json
import math
import os
import pathlib
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))                 # contract.py / contract_io.py (ours); gen dir stays first

DATA = pathlib.Path(os.environ.get("RECALLSTORM_DATA", ROOT / "data"))
LA = ZoneInfo("America/Los_Angeles")


def read_jsonl(name: str) -> list[dict]:
    p = DATA / name
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def read_labels() -> dict[str, str]:
    p = DATA / "labels.csv"
    if not p.exists():
        return {}
    with open(p, newline="") as fh:
        return {r["sku_id"]: r["truth"].strip() for r in csv.DictReader(fh)}


def la(y, mo, d, h=0, mi=0) -> datetime:
    return datetime(y, mo, d, h, mi, tzinfo=LA)


def make_sku(ingredients: str, *, sku_id="SKU_T", is_food=True, is_drug=False, category="candy",
             case_units=12, cube=1.0, weight=10.0):
    from contract import Sku
    return Sku(sku_id=sku_id, gtin="00000000000000", name=f"test {sku_id}", brand="Test", category=category,
               ingredients=ingredients, is_food=is_food, is_ingested_drug=is_drug, case_units=case_units,
               case_cube_ft3=cube, case_weight_lb=weight)


def code(v) -> str:
    """Enum or str -> its string value."""
    return getattr(v, "value", v)


@pytest.fixture(scope="session")
def pack():
    from contract import load_datapack
    return load_datapack(str(DATA))


@pytest.fixture(scope="session")
def labels():
    return read_labels()


@pytest.fixture(scope="session")
def rules(pack):
    return list(pack.rules)


@pytest.fixture(scope="session")
def pulled_cases(pack, labels):
    """(store_id, sku_id) -> cases for every truth-PULL facing: ceil(units / case_units)."""
    by_id = {s.sku_id: s for s in pack.skus}
    out: dict[tuple[str, str], int] = {}
    for f in pack.facings:
        if labels.get(f.sku_id) == "PULL" and f.sku_id in by_id:
            k = (f.store_id, f.sku_id)
            out[k] = out.get(k, 0) + max(1, math.ceil(f.units / max(1, by_id[f.sku_id].case_units)))
    return out


@pytest.fixture(scope="session")
def sub_demand(pack, labels):
    """(store_id, sub_sku_id) -> cases wanted: first substitute of each truth-PULL facing."""
    by_id = {s.sku_id: s for s in pack.skus}
    out: dict[tuple[str, str], int] = {}
    for f in pack.facings:
        if labels.get(f.sku_id) == "PULL":
            subs = pack.substitutes.get(f.sku_id) or []
            if subs and subs[0] in by_id:
                k = (f.store_id, subs[0])
                out[k] = out.get(k, 0) + max(1, math.ceil(f.units / max(1, by_id[subs[0]].case_units)))
    return out
