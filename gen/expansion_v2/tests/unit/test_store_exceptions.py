"""Unit tests for recallstorm.store.exceptions."""
from contract import ExceptionKind, StoreNote
from recallstorm.core.jsonl import validate_record
from recallstorm.store.exceptions import (
    dsd_vendor_pull,
    endcap_display,
    exception_kind_for_text,
    exceptions_for_store,
    note_to_exception,
    parse_note,
    pickup_totes,
    resolve_exception,
    topstock,
)


def test_store_exceptions_all_six_kinds():
    notes = [
        StoreNote("N0000", "SAMS4735", "Endcap 16 holds a vendor Halloween display; candy there is not on the planogram."),
        StoreNote("N0003", "SAMS4767", "Frito-Lay DSD rep restocks Tuesdays; DSD items are vendor-pulled, do not pack for DC return."),
        StoreNote("N0006", "SAMS6405", "Topstock above aisle 12 has overflow cases of baking decorations."),
        StoreNote("N0009", "SAMS6621", "Online pickup totes staged in backroom bay 4 may contain affected items."),
        StoreNote("N0012", "WM1563", "Aisle 5 moved to garden center during remodel; locations are not on planogram."),
        StoreNote("N0015", "WM1574", "Store-brand frosting labels are smudged from a printer fault; check ingredients by hand."),
    ]
    assert endcap_display(notes[0]) is True
    assert dsd_vendor_pull(notes[1]) is True
    assert topstock(notes[2]) is True
    assert pickup_totes(notes[3]) is True
    assert exception_kind_for_text(notes[4].text) == ExceptionKind.NOT_ON_PLANOGRAM
    assert exception_kind_for_text(notes[5].text) == ExceptionKind.UNCLEAR_LABEL

    for n in notes:
        p = parse_note(n)
        assert p["store_id"] == n.store_id
        rec = note_to_exception(n, ["TSK-1"])
        assert validate_record(rec, "exception") == []
    assert len(exceptions_for_store(notes, "SAMS4735")) == 1
    assert "DSD" in resolve_exception(ExceptionKind.DSD_VENDOR_PULL, notes[1])
