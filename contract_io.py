"""OURS. Reads data/*.jsonl into contract dataclasses. Not generated."""
from __future__ import annotations
import json, pathlib
from datetime import datetime
from contract import (Sku, Store, StoreFormat, Location, Facing, Associate, Truck, DcStock,
                      StoreNote, Rule, DataPack)


def _rows(d: pathlib.Path, name: str) -> list[dict]:
    p = d / name
    if not p.exists():
        return []
    # keys starting with "_" are provenance extras (e.g. "_real", "_src"), not contract fields
    return [{k: v for k, v in json.loads(line).items() if not k.startswith("_")}
            for line in p.read_text().splitlines() if line.strip()]


def _dt(s: str) -> datetime:
    return datetime.fromisoformat(s)


def load(data_dir: str, scenario: str = "ca_red3") -> DataPack:
    d = pathlib.Path(data_dir)
    skus = [Sku(**r) for r in _rows(d, "skus.jsonl")]
    stores = [Store(**{**r, "format": StoreFormat(r["format"])}) for r in _rows(d, "stores.jsonl")]
    facings = [Facing(**{**r, "loc": Location(**r["loc"])}) for r in _rows(d, "facings.jsonl")]
    associates = [Associate(**{**r, "shift_start": _dt(r["shift_start"]), "shift_end": _dt(r["shift_end"])})
                  for r in _rows(d, "associates.jsonl")]
    trucks = [Truck(**{**r, "depart": _dt(r["depart"])}) for r in _rows(d, "trucks.jsonl")]
    dc_stock = [DcStock(**r) for r in _rows(d, "dc_stock.jsonl")]
    subs_p = d / "substitutes.json"
    substitutes = json.loads(subs_p.read_text()) if subs_p.exists() else {}
    notes = [StoreNote(**r) for r in _rows(d, "notes.jsonl")]
    rules = [Rule(**{**r, "aliases": tuple(r["aliases"]), "jurisdictions": tuple(r["jurisdictions"]),
                     "applies_to": tuple(r["applies_to"]), "effective": _dt(r["effective"])})
             for r in _rows(d, "rules.jsonl")]
    sc_p = d / f"scenario_{scenario}.json"
    as_of = _dt(json.loads(sc_p.read_text())["as_of"]) if sc_p.exists() else datetime.now().astimezone()
    return DataPack(skus=skus, stores=stores, facings=facings, associates=associates, trucks=trucks,
                    dc_stock=dc_stock, substitutes=substitutes, notes=notes, rules=rules, as_of=as_of)
