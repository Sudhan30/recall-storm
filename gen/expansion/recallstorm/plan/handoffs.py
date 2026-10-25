"""Build FLOATER, SUB_TRANSFER, and RETURN_CONSOLIDATION handoff records."""
from __future__ import annotations

from dataclasses import dataclass
from contract import Allocation, HandoffKind, RouteManifest
from recallstorm.core.ids import make_handoff_id
from recallstorm.core.jsonl import record_with_src


@dataclass(frozen=True)
class HandoffBuilder:
    """Builds cross-entity handoff records for plan.jsonl."""

    default_window: tuple[str, str]


def floater_handoff(
    associate_id: str,
    store_id: str,
    window: list[str] | tuple[str, str],
    task_ids: list[str],
    seq: int = 0,
) -> dict:
    """Create a validated FLOATER handoff record."""
    hid = make_handoff_id(HandoffKind.FLOATER, associate_id, store_id, seq)
    payload = {
        "handoff_id": hid,
        "kind": HandoffKind.FLOATER.value,
        "from_id": associate_id,
        "to_id": store_id,
        "window": [str(window[0]), str(window[1])],
        "qty": max(1, len(task_ids)),
        "ref_ids": list(task_ids),
    }
    return record_with_src(payload, "handoff", "recallstorm/plan/handoffs.py")


def sub_transfer_handoff(
    dc_id: str,
    store_id: str,
    window: list[str] | tuple[str, str],
    cases: int,
    alloc_id: str,
    seq: int = 0,
) -> dict:
    """Create a validated SUB_TRANSFER handoff record."""
    hid = make_handoff_id(HandoffKind.SUB_TRANSFER, dc_id, store_id, seq)
    payload = {
        "handoff_id": hid,
        "kind": HandoffKind.SUB_TRANSFER.value,
        "from_id": dc_id,
        "to_id": store_id,
        "window": [str(window[0]), str(window[1])],
        "qty": cases,
        "ref_ids": [alloc_id],
    }
    return record_with_src(payload, "handoff", "recallstorm/plan/handoffs.py")


def return_consolidation(
    store_id: str,
    dc_id: str,
    window: list[str] | tuple[str, str],
    cases: int,
    manifest_id: str,
    seq: int = 0,
) -> dict:
    """Create a validated RETURN_CONSOLIDATION handoff record."""
    hid = make_handoff_id(HandoffKind.RETURN_CONSOLIDATION, store_id, dc_id, seq)
    payload = {
        "handoff_id": hid,
        "kind": HandoffKind.RETURN_CONSOLIDATION.value,
        "from_id": store_id,
        "to_id": dc_id,
        "window": [str(window[0]), str(window[1])],
        "qty": cases,
        "ref_ids": [manifest_id],
    }
    return record_with_src(payload, "handoff", "recallstorm/plan/handoffs.py")


def build_handoffs(
    allocations: list[Allocation],
    manifests: list[RouteManifest],
    floater_dispatches: list[dict] | None = None,
    default_window: list[str] | tuple[str, str] | None = None,
) -> list[dict]:
    """Build all FLOATER, SUB_TRANSFER, and RETURN_CONSOLIDATION handoff records."""
    win = list(default_window) if default_window else ["2026-12-31T06:00:00-08:00", "2026-12-31T12:00:00-08:00"]
    out: list[dict] = []

    for idx, d in enumerate(floater_dispatches or []):
        out.append(
            floater_handoff(
                d["associate_id"],
                d["store_id"],
                d.get("window", win),
                d.get("task_ids", []),
                idx,
            )
        )

    for idx, a in enumerate(allocations):
        out.append(sub_transfer_handoff(a.dc_id, a.store_id, win, a.qty_cases, a.alloc_id, idx))

    seq = 0
    for m in manifests:
        for st in m.stops:
            seq += 1
            out.append(return_consolidation(st.store_id, m.dc_id, win, st.cases, m.manifest_id, seq))

    return out


def handoff_to_record(h: dict) -> dict:
    """Validate and return a handoff record."""
    payload = {k: v for k, v in h.items() if k not in ("type", "src")}
    return record_with_src(payload, "handoff", "recallstorm/plan/handoffs.py")


def pair_handoffs(handoffs: list[dict]) -> dict[str, list[dict]]:
    """Group handoffs by kind."""
    out: dict[str, list[dict]] = {}
    for h in handoffs:
        k = str(h.get("kind", ""))
        out.setdefault(k, []).append(h)
    return out


def handoff_windows(handoffs: list[dict]) -> list[list[str]]:
    """Return all handoff windows."""
    return [list(h["window"]) for h in handoffs if "window" in h]


def handoff_summary(handoffs: list[dict]) -> dict:
    """Summarize handoffs by kind and total quantity."""
    grouped = pair_handoffs(handoffs)
    return {
        "total_handoffs": len(handoffs),
        "by_kind": {k: len(v) for k, v in grouped.items()},
    }
