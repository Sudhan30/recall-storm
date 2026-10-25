"""Parse free-text StoreNotes into structured ExceptionKinds."""
from __future__ import annotations

from contract import ExceptionKind, StoreNote
from recallstorm.core.ids import make_exc_id


def exception_kind_for_text(text: str) -> ExceptionKind:
    """Classify a free-text store note into one of the six contract ExceptionKinds."""
    low = (text or "").lower()
    if "dsd" in low or "vendor-pulled" in low or "frito-lay" in low:
        return ExceptionKind.DSD_VENDOR_PULL
    if "endcap" in low or "display" in low:
        return ExceptionKind.ENDCAP_DISPLAY
    if "topstock" in low or "overflow" in low:
        return ExceptionKind.TOPSTOCK
    if "tote" in low or "pickup" in low or "online" in low:
        return ExceptionKind.PICKUP_TOTES
    if "smudged" in low or "printer fault" in low or "unreadable" in low or "by hand" in low:
        return ExceptionKind.UNCLEAR_LABEL
    if "planogram" in low or "remodel" in low or "garden center" in low or "moved" in low:
        return ExceptionKind.NOT_ON_PLANOGRAM
    return ExceptionKind.NOT_ON_PLANOGRAM


def dsd_vendor_pull(note: StoreNote) -> bool:
    """Return True if note indicates a DSD vendor pull exception."""
    return exception_kind_for_text(note.text) == ExceptionKind.DSD_VENDOR_PULL


def endcap_display(note: StoreNote) -> bool:
    """Return True if note indicates an off-planogram endcap display."""
    return exception_kind_for_text(note.text) == ExceptionKind.ENDCAP_DISPLAY


def topstock(note: StoreNote) -> bool:
    """Return True if note indicates topstock overflow cases."""
    return exception_kind_for_text(note.text) == ExceptionKind.TOPSTOCK


def pickup_totes(note: StoreNote) -> bool:
    """Return True if note indicates staged online pickup totes."""
    return exception_kind_for_text(note.text) == ExceptionKind.PICKUP_TOTES


def resolve_exception(kind: ExceptionKind, note: StoreNote) -> str:
    """Return the operational resolution instruction for kind and note."""
    resolutions = {
        ExceptionKind.DSD_VENDOR_PULL: "Stage in DSD vendor cage for route driver credit; exclude from DC return truck.",
        ExceptionKind.ENDCAP_DISPLAY: "Sweep seasonal/vendor endcap display and pull all affected units.",
        ExceptionKind.TOPSTOCK: "Use topstock ladder cart to pull overflow cases above the aisle.",
        ExceptionKind.PICKUP_TOTES: "Intercept and audit staged online pickup totes in backroom bay before customer handoff.",
        ExceptionKind.NOT_ON_PLANOGRAM: "Locate relocated aisle/flex fixture from store remodel map and sweep affected SKUs.",
        ExceptionKind.UNCLEAR_LABEL: "Hold smudged/illegible units for manual QA ingredient verification.",
    }
    return resolutions[kind]


def parse_note(note: StoreNote) -> dict:
    """Parse a StoreNote into its ExceptionKind and resolution."""
    kind = exception_kind_for_text(note.text)
    return {
        "exc_id": make_exc_id(note.store_id, note.note_id),
        "store_id": note.store_id,
        "note_id": note.note_id,
        "kind": kind.value,
        "resolution": resolve_exception(kind, note),
    }


def note_to_exception(note: StoreNote, task_ids: list[str] | None = None) -> dict:
    """Convert a StoreNote into a plan.jsonl 'exception' record."""
    parsed = parse_note(note)
    return {
        "type": "exception",
        "exc_id": parsed["exc_id"],
        "store_id": parsed["store_id"],
        "kind": parsed["kind"],
        "note_id": parsed["note_id"],
        "resolution": parsed["resolution"],
        "task_ids": list(task_ids or []),
        "src": "recallstorm/store/exceptions.py",
    }


def exceptions_for_store(notes: list[StoreNote], store_id: str) -> list[dict]:
    """Return all exception records for store_id."""
    return [note_to_exception(n) for n in notes if n.store_id == store_id]
