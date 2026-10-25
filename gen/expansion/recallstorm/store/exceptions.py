"""Classify free-text StoreNotes into contract ExceptionKind values and resolution steps."""
from __future__ import annotations

from contract import ExceptionKind, StoreNote
from recallstorm.core.ids import make_exc_id
from recallstorm.core.jsonl import record_with_src

_RESOLUTIONS: dict[ExceptionKind, str] = {
    ExceptionKind.DSD_VENDOR_PULL: "Notify DSD vendor rep to pull and credit; exclude from DC return manifest.",
    ExceptionKind.ENDCAP_DISPLAY: "Sweep promotional endcap display and pull all affected units.",
    ExceptionKind.TOPSTOCK: "Inspect topstock riser above aisle and pull overflow cases.",
    ExceptionKind.PICKUP_TOTES: "Audit staged online pickup totes in backroom and remove affected items.",
    ExceptionKind.NOT_ON_PLANOGRAM: "Inspect relocated/remodel aisle and pull non-planogram facings.",
    ExceptionKind.UNCLEAR_LABEL: "Place smudged/unclear items on HOLD_VERIFY pending manual inspection.",
}


def exception_kind_for_text(text: str) -> ExceptionKind:
    """Classify a free-text note into one of the six contract ExceptionKind enum values."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Note text must be a non-empty string")
    low = text.lower()
    if "dsd" in low or "frito-lay" in low or "vendor-pulled" in low:
        return ExceptionKind.DSD_VENDOR_PULL
    if "endcap" in low:
        return ExceptionKind.ENDCAP_DISPLAY
    if "topstock" in low or "overflow cases" in low:
        return ExceptionKind.TOPSTOCK
    if "totes" in low or "online pickup" in low:
        return ExceptionKind.PICKUP_TOTES
    if "smudged" in low or "printer fault" in low or "unreadable" in low or "by hand" in low:
        return ExceptionKind.UNCLEAR_LABEL
    if "not on planogram" in low or "not on the planogram" in low or "remodel" in low or "garden center" in low:
        return ExceptionKind.NOT_ON_PLANOGRAM
    return ExceptionKind.NOT_ON_PLANOGRAM


def resolve_exception(kind: ExceptionKind) -> str:
    """Return the standard operational resolution instruction for an ExceptionKind."""
    if not isinstance(kind, ExceptionKind):
        kind = ExceptionKind(str(kind))
    return _RESOLUTIONS[kind]


def parse_note(note: StoreNote) -> dict:
    """Parse a StoreNote into a structured dictionary with its classified ExceptionKind."""
    if not isinstance(note, StoreNote):
        raise TypeError("note must be a StoreNote")
    kind = exception_kind_for_text(note.text)
    return {
        "exc_id": make_exc_id(note.store_id, note.note_id, kind),
        "store_id": note.store_id,
        "kind": kind.value,
        "note_id": note.note_id,
        "resolution": resolve_exception(kind),
    }


def dsd_vendor_pull(note: StoreNote) -> dict:
    """Build a DSD_VENDOR_PULL exception dict from a StoreNote."""
    return {**parse_note(note), "kind": ExceptionKind.DSD_VENDOR_PULL.value}


def endcap_display(note: StoreNote) -> dict:
    """Build an ENDCAP_DISPLAY exception dict from a StoreNote."""
    return {**parse_note(note), "kind": ExceptionKind.ENDCAP_DISPLAY.value}


def topstock(note: StoreNote) -> dict:
    """Build a TOPSTOCK exception dict from a StoreNote."""
    return {**parse_note(note), "kind": ExceptionKind.TOPSTOCK.value}


def pickup_totes(note: StoreNote) -> dict:
    """Build a PICKUP_TOTES exception dict from a StoreNote."""
    return {**parse_note(note), "kind": ExceptionKind.PICKUP_TOTES.value}


def note_to_exception(note: StoreNote, task_ids: list[str] | None = None) -> dict:
    """Convert a StoreNote and linked task_ids into a validated 'exception' plan.jsonl record."""
    base = parse_note(note)
    base["task_ids"] = list(task_ids) if task_ids else []
    return record_with_src(base, "exception", "recallstorm/store/exceptions.py")


def exceptions_for_store(notes: list[StoreNote], store_id: str) -> list[dict]:
    """Return all parsed exception records for store_id."""
    return [note_to_exception(n) for n in notes if n.store_id == store_id]
