"""OURS. Baseline D return routing: first-fit by case, stores in store_id order, splitting across trucks."""
from __future__ import annotations

from collections import defaultdict

from contract import RouteManifest, Sku, Stop, Store, Truck

from ._src import src_of
SRC = src_of(__file__)


def pack_returns(pulled_cases: dict[tuple[str, str], int], skus: list[Sku], trucks: list[Truck],
                 stores: list[Store]) -> list[RouteManifest]:
    sk = {s.sku_id: s for s in skus}
    dc_of = {s.store_id: s.dc_id for s in stores}
    by_dc: dict[str, dict[str, list[tuple[str, int]]]] = defaultdict(lambda: defaultdict(list))
    for (sid, sku_id), n in pulled_cases.items():
        if n > 0:
            by_dc[dc_of[sid]][sid].append((sku_id, int(n)))
    trucks_by_dc: dict[str, list[Truck]] = defaultdict(list)
    for t in trucks:
        trucks_by_dc[t.dc_id].append(t)

    out: list[RouteManifest] = []
    for dc in sorted(by_dc):
        fleet = sorted(trucks_by_dc[dc], key=lambda t: t.truck_id)
        loads: list[dict[str, list[float]]] = []      # per truck: store -> [cases, cube, weight]
        ti, cube_used, wt_used = 0, 0.0, 0.0
        if not fleet:
            raise ValueError(f"no trucks at {dc}")
        loads.append(defaultdict(lambda: [0, 0.0, 0.0]))
        for sid in sorted(by_dc[dc]):
            for sku_id, n in sorted(by_dc[dc][sid]):
                c, w = sk[sku_id].case_cube_ft3, sk[sku_id].case_weight_lb
                while n > 0:
                    t = fleet[ti]
                    fit_c = int((t.cube_ft3 - cube_used + 1e-9) // c) if c > 0 else n
                    fit_w = int((t.weight_lb - wt_used + 1e-9) // w) if w > 0 else n
                    k = min(n, fit_c, fit_w)
                    if k <= 0:
                        ti += 1
                        if ti >= len(fleet):
                            raise ValueError(f"not enough truck capacity at {dc}")
                        cube_used = wt_used = 0.0
                        loads.append(defaultdict(lambda: [0, 0.0, 0.0]))
                        continue
                    st = loads[-1][sid]
                    st[0] += k; st[1] += k * c; st[2] += k * w
                    cube_used += k * c; wt_used += k * w
                    n -= k
        for i, load in enumerate(loads):
            stops = tuple(Stop(store_id=sid, cases=int(v[0]), cube_ft3=v[1], weight_lb=v[2])
                          for sid, v in sorted(load.items()) if v[0] > 0)
            if not stops:
                continue
            t = fleet[i]
            out.append(RouteManifest(manifest_id=f"MF-{t.truck_id}", truck_id=t.truck_id, dc_id=dc,
                                     stops=stops, depart=t.depart))
    return out
