"""Unit tests for recallstorm.recall_lots.best_by_window."""
from recallstorm.recall_lots.best_by_window import (
    DateWindowSpec,
    ExpirationFormatParser,
    calculate_shelf_life_backdate_lot,
    check_freeze_by_extension,
    convert_julian_to_calendar_date,
    evaluate_inclusive_date_range,
    flag_unreadable_inkjet_dates,
    handle_month_year_only_stamps,
    match_pack_date_to_best_by,
    normalize_two_digit_year,
    parse_stamped_date_string,
    validate_window_chronology,
)


def test_best_by_window():
    assert DateWindowSpec().status == "ACTIVE"
    assert ExpirationFormatParser().status == "ACTIVE"
    assert normalize_two_digit_year(27) == 2027
    assert parse_stamped_date_string("08/15/26") == "2026-08-15"
    assert evaluate_inclusive_date_range("2026-06-15", "2026-06-01", "2026-06-30") is True
    assert convert_julian_to_calendar_date(2026, 32) == "2026-02-01"
    assert check_freeze_by_extension("2026-01-01", 10) == "2026-01-11"
    assert flag_unreadable_inkjet_dates("SMUDGE???") is True
    assert calculate_shelf_life_backdate_lot("2026-01-11", 10) == "2026-01-01"
    assert match_pack_date_to_best_by("2026-01-01", "2026-01-11", 10) is True
    assert handle_month_year_only_stamps(2027, 2) == ("2027-02-01", "2027-02-28")
    assert validate_window_chronology("2026-01-01", "2026-12-31") is True
