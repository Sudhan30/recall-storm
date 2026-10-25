"""Unit tests for recallstorm.core.logging_setup."""
from recallstorm.core.logging_setup import (
    JsonlLogHandler,
    configure_logging,
    flush_all,
    get_logger,
    log_event,
    log_timing,
    redact_text,
    set_level,
    with_context,
)


def test_logging_and_jsonl_handler(tmp_path):
    log_file = tmp_path / "run.jsonl"
    handler = configure_logging("DEBUG", log_file)
    assert isinstance(handler, JsonlLogHandler)
    logger = get_logger("recallstorm.test")
    ev = log_event(logger, "test_start", {"store": "WM1563"})
    assert ev["event_type"] == "test_start"
    tm = log_timing(logger, "eval", 12.3456)
    assert tm["payload"]["elapsed_ms"] == 12.346
    adapter = with_context(logger, run_id="R1")
    adapter.info("Contact rep@vendor.com or 555-123-4567")
    assert flush_all() >= 1
    lines = log_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) >= 3
    assert "[REDACTED_EMAIL]" in lines[-1]
    assert "[REDACTED_PHONE]" in lines[-1]


def test_set_level_and_redact():
    logger = get_logger("recallstorm.level")
    set_level(logger, "WARNING")
    assert logger.level == 30
    assert redact_text("email a@b.co phone 800-555-0199") == "email [REDACTED_EMAIL] phone [REDACTED_PHONE]"
