"""Build handoff records for FLOATER, SUB_TRANSFER, and RETURN_CONSOLIDATION."""
from __future__ import annotations

from dataclasses import dataclass

from contract import Allocation, HandoffKind
from recallstorm.core.ids import make_handoff_id


@dataclass
class HandoffBuilder:
    """Builder for plan.jsonl handoff records."""

    default_window: list[str]


def floater_handoff(
    associate_id: str, store_id: str, window: list[str], task_ids: list[str], seq: int = 0
) -> dict:
    """Create a FLOATER handoff record."""
    return {
        "type": "handoff",
        "handoff_id": make_handoff_id(HandoffKind.FLOATER.value, associate_id, store_id, seq),
        "kind": HandoffKind.FLOATER.value,
        "from_id": associate_id,
        "to_id": store_id,
        "window": list(window),
        "qty": max(1, len(task_ids)),
        "ref_ids": list(task_ids),
        "src": "recallstorm/plan/handoffs.py",
    }


def sub_transfer_handoff(alloc: Allocation, window: list[str], seq: int = 0) -> dict:
    """Create a SUB_TRANSFER handoff record referencing alloc.alloc_id."""
    return {
        "type": "handoff",
        "handoff_id": make_handoff_id(HandoffKind.SUB_TRANSFER.value, alloc.dc_id, alloc.store_id, seq),
        "kind": HandoffKind.SUB_TRANSFER.value,
        "from_id": alloc.dc_id,
        "to_id": alloc.store_id,
        "window": list(window),
        "qty": alloc.qty_cases,
        "ref_ids": [alloc.alloc_id],
        "src": "recallstorm/plan/handoffs.py",
    }


def return_consolidation(
    store_id: str, dc_id: str, window: list[str], cases: int, manifest_id: str, seq: int = 0
) -> dict:
    """Create a RETURN_CONSOLIDATION handoff record referencing manifest_id."""
    return {
        "type": "handoff",
        "handoff_id": make_handoff_id(HandoffKind.RETURN_CONSOLIDATION.value, store_id, dc_id, seq),
        "kind": HandoffKind.RETURN_CONSOLIDATION.value,
        "from_id": store_id,
        "to_id": dc_id,
        "window": list(window),
        "qty": cases,
        "ref_ids": [manifest_id],
        "src": "recallstorm/plan/handoffs.py",
    }


def build_handoffs(
    allocations: list[Allocation],
    manifests: list[dict],
    floater_dispatches: list[dict],
    window: list[str],
) -> list[dict]:
    """Build all SUB_TRANSFER, RETURN_CONSOLIDATION, and FLOATER handoff records."""
    out: list[dict] = []
    for idx, a in enumerate(allocations):
        out.append(sub_transfer_handoff(a, window, seq=idx))
    for idx, m in enumerate(manifests):
        dc_id = str(m.get("dc_id", "DC_NORTH"))
        mid = str(m.get("manifest_id", "MNF-0"))
        for s_idx, stop in enumerate(m.get("stops", [])):
            st_id = stop.get("store_id") if isinstance(stop, dict) else getattr(stop, "store_id", "")
            cases = int(stop.get("cases", 1) if isinstance(stop, dict) else getattr(stop, "cases", 1))
            out.append(return_consolidation(st_id, dc_id, window, cases, mid, seq=idx * 100 + s_idx))
    for idx, fd in enumerate(floater_dispatches):
        out.append(
            floater_handoff(
                str(fd["associate_id"]),
                str(fd["store_id"]),
                list(fd.get("window", window)),
                list(fd.get("task_ids", [])),
                seq=idx,
            )
        )
    return out


def handoff_to_record(h: dict) -> dict:
    """Ensure handoff dictionary has 'type' and 'src'."""
    out = dict(h)
    out["type"] = "handoff"
    out.setdefault("src", "recallstorm/plan/handoffs.py")
    return out


def pair_handoffs(handoffs: list[dict]) -> dict[str, list[dict]]:
    """Group handoffs by HandoffKind value."""
    out = {k.value: [] for k in HandoffKind}
    for h in handoffs:
        out.setdefault(str(h.get("kind", "")), []).append(h)
    return out


def handoff_windows(handoffs: list[dict]) -> list[list[str]]:
    """Return all window intervals from handoffs."""
    return [h["window"] for h in handoffs if "window" in h]


def handoff_summary(handoffs: list[dict]) -> dict:
    """Summarize handoffs by kind."""
    paired = pair_handoffs(handoffs)
    return {k: len(v) for k, v in paired.items()}
