"""Structured JSONL logging and PII redaction."""
from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE_RE = re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b")


class JsonlLogHandler(logging.Handler):
    """Logging handler that writes structured JSONL lines to a file or memory buffer."""

    def __init__(self, jsonl_path: str | None = None):
        super().__init__()
        self.jsonl_path = jsonl_path
        self.records: list[dict] = []

    def emit(self, record: logging.LogRecord) -> None:
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": redact_text(record.getMessage()),
        }
        extra_fields = getattr(record, "structured_fields", None)
        if isinstance(extra_fields, dict):
            entry.update(extra_fields)
        self.records.append(entry)
        if self.jsonl_path:
            p = Path(self.jsonl_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            with p.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, sort_keys=True) + "\n")


def get_logger(name: str = "recallstorm") -> logging.Logger:
    """Return a named logger instance."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Logger name must be a non-empty string")
    return logging.getLogger(name)


def configure_logging(level: str = "INFO", jsonl_path: str | None = None) -> logging.Logger:
    """Configure the root recallstorm logger with a JsonlLogHandler."""
    logger = get_logger("recallstorm")
    set_level(logger, level)
    logger.handlers.clear()
    handler = JsonlLogHandler(jsonl_path=jsonl_path)
    logger.addHandler(handler)
    return logger


def redact_text(text: str) -> str:
    """Redact emails and US phone numbers from free text."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    res = _EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    res = _PHONE_RE.sub("[REDACTED_PHONE]", res)
    return res


def log_event(logger: logging.Logger, event: str, **fields) -> dict:
    """Log a structured event and return the emitted dictionary."""
    if not isinstance(event, str) or not event.strip():
        raise ValueError("event must be a non-empty string")
    payload = {"event": event, **fields}
    logger.info(event, extra={"structured_fields": payload})
    return payload


def log_timing(logger: logging.Logger, op: str, duration_ms: float, **fields) -> dict:
    """Log a timing measurement in milliseconds."""
    if duration_ms < 0:
        raise ValueError("duration_ms must be non-negative")
    return log_event(logger, "timing", op=op, duration_ms=round(float(duration_ms), 3), **fields)


def with_context(logger: logging.Logger, **ctx) -> dict:
    """Create a context dictionary bound to the given logger name."""
    return {"logger": logger.name, "context": ctx}


def set_level(logger: logging.Logger, level: str) -> None:
    """Set the logging level by name."""
    lvl = getattr(logging, str(level).upper(), None)
    if not isinstance(lvl, int):
        raise ValueError(f"Unknown log level: {level!r}")
    logger.setLevel(lvl)


def flush_all(logger: logging.Logger | None = None) -> None:
    """Flush all handlers on the given or default logger."""
    target = logger or get_logger("recallstorm")
    for h in target.handlers:
        h.flush()
