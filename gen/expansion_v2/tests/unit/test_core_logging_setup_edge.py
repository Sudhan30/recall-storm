"""Edge case tests for recallstorm.core.logging_setup."""
import pytest
from recallstorm.core.logging_setup import (
     configure_logging,
    get_logger,
    log_event,
    log_timing,
    redact_text,
    set_level,
)


def test_logging_invalid_inputs():
    logger = configure_logging()
    with pytest.raises(ValueError):
        get_logger("")
    with pytest.raises(ValueError):
        log_event(logger, "")
    with pytest.raises(ValueError):
        log_timing(logger, "op", -1.0)
    with pytest.raises(ValueError):
        set_level(logger, "NOT_A_LEVEL")
    with pytest.raises(TypeError):
        redact_text(123)  # type: ignore[arg-type]
