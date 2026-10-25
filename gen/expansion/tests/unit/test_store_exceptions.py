"""Unit tests for recallstorm.store.exceptions."""
from contract import ExceptionKind, StoreNote
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


def test_all_six_exception_kinds():
    samples = [
        ("N1", "Endcap 16 holds a vendor Halloween display; candy there is not on the planogram.", ExceptionKind.ENDCAP_DISPLAY),
        ("N2", "Frito-Lay DSD rep restocks Tuesdays; DSD items are vendor-pulled.", ExceptionKind.DSD_VENDOR_PULL),
        ("N3", "Topstock above aisle 12 has overflow cases of baking decorations.", ExceptionKind.TOPSTOCK),
        ("N4", "Online pickup totes staged in backroom bay 4 may contain affected items.", ExceptionKind.PICKUP_TOTES),
        ("N5", "Aisle 5 moved to garden center during remodel; locations are not on planogram.", ExceptionKind.NOT_ON_PLANOGRAM),
        ("N6", "Store-brand frosting labels are smudged from a printer fault; check ingredients by hand.", ExceptionKind.UNCLEAR_LABEL),
    ]
    notes = [StoreNote(nid, "WM1", txt) for nid, txt, _ in samples]
    for (nid, txt, expected_kind), note in zip(samples, notes):
        assert exception_kind_for_text(txt) == expected_kind
        assert len(resolve_exception(expected_kind)) > 10
        rec = note_to_exception(note, ["TSK-1"])
        assert rec["kind"] == expected_kind.value
        assert rec["task_ids"] == ["TSK-1"]

    assert dsd_vendor_pull(notes[1])["kind"] == "DSD_VENDOR_PULL"
    assert endcap_display(notes[0])["kind"] == "ENDCAP_DISPLAY"
    assert topstock(notes[2])["kind"] == "TOPSTOCK"
    assert pickup_totes(notes[3])["kind"] == "PICKUP_TOTES"
    assert parse_note(notes[0])["store_id"] == "WM1"
    assert len(exceptions_for_store(notes, "WM1")) == 6
