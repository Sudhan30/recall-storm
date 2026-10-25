"""OURS. Baseline D allocation: greedy per (DC, substitute) in store_id order."""
from __future__ import annotations

from collections import defaultdict

from contract import Allocation, DcStock, Store

from ._src import src_of
SRC = src_of(__file__)


def allocate_substitutes(demand: dict[tuple[str, str], int], stock: list[DcStock],
                         stores: list[Store]) -> list[Allocation]:
    dc_of = {s.store_id: s.dc_id for s in stores}
    avail = {(s.dc_id, s.sku_id): s.cases for s in stock}
    groups: dict[tuple[str, str], list[tuple[str, int]]] = defaultdict(list)
    for (sid, sub), q in demand.items():
        if sid in dc_of and int(q) > 0:
            groups[(dc_of[sid], sub)].append((sid, int(q)))
    out: list[Allocation] = []
    for (dc, sub) in sorted(groups):
        left = avail.get((dc, sub), 0)
        for sid, q in sorted(groups[(dc, sub)]):
            give = min(q, left)
            if give <= 0:
                continue
            left -= give
            out.append(Allocation(alloc_id=f"AL-{dc}-{sub}-{sid}", dc_id=dc, sub_sku_id=sub, store_id=sid,
                                  qty_cases=give, dc_balance_after=left))
    return out
