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


def test_logging_setup_and_redaction(tmp_path):
    log_file = tmp_path / "run.jsonl"
    logger = configure_logging("DEBUG", str(log_file))
    assert get_logger("recallstorm") is logger
    ev = log_event(logger, "sku_checked", sku_id="FDC1034191")
    assert ev["sku_id"] == "FDC1034191"
    tm = log_timing(logger, "evaluate", 12.345)
    assert tm["duration_ms"] == 12.345
    ctx = with_context(logger, run_id="RUN-1")
    assert ctx["context"]["run_id"] == "RUN-1"
    set_level(logger, "WARNING")
    flush_all(logger)
    assert log_file.exists()

    redacted = redact_text("Contact jane@example.com or 555-123-4567 now")
    assert "[REDACTED_EMAIL]" in redacted
    assert "[REDACTED_PHONE]" in redacted
    assert isinstance(logger.handlers[0], JsonlLogHandler)
