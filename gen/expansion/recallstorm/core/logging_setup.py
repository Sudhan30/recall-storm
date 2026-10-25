"""Structured logging, JSONL handler, and PII redaction for Recall Storm."""
from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path

_HANDLERS: list[logging.Handler] = []
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE_RE = re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b")


class JsonlLogHandler(logging.Handler):
    """Logging handler that writes structured JSON lines to a file or buffer."""

    def __init__(self, path: str | Path | None = None) -> None:
        super().__init__()
        self.path = Path(path) if path else None
        self.records: list[dict] = []

    def emit(self, record: logging.LogRecord) -> None:
        entry = {
            "ts": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": redact_text(record.getMessage()),
        }
        self.records.append(entry)
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, sort_keys=True) + "\n")


def get_logger(name: str = "recallstorm") -> logging.Logger:
    """Return a named logger."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("logger name must be a non-empty string")
    return logging.getLogger(name.strip())


def configure_logging(level: str | int = "INFO", jsonl_path: str | Path | None = None) -> JsonlLogHandler:
    """Configure the root recallstorm logger and attach a JsonlLogHandler."""
    logger = get_logger("recallstorm")
    set_level(logger, level)
    handler = JsonlLogHandler(jsonl_path)
    logger.addHandler(handler)
    _HANDLERS.append(handler)
    return handler


def redact_text(text: str) -> str:
    """Redact emails and phone numbers from log text."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    out = _EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    out = _PHONE_RE.sub("[REDACTED_PHONE]", out)
    return out


def log_event(logger: logging.Logger, event_type: str, payload: dict | None = None) -> dict:
    """Log a structured event and return the event dictionary."""
    if not isinstance(event_type, str) or not event_type.strip():
        raise ValueError("event_type must be a non-empty string")
    rec = {
        "event_type": event_type.strip(),
        "payload": dict(payload) if payload else {},
    }
    logger.info(json.dumps(rec, sort_keys=True))
    return rec


def log_timing(logger: logging.Logger, op_name: str, elapsed_ms: float) -> dict:
    """Log an operation timing metric."""
    if not isinstance(op_name, str) or not op_name.strip():
        raise ValueError("op_name must be a non-empty string")
    if not isinstance(elapsed_ms, (int, float)) or elapsed_ms < 0:
        raise ValueError("elapsed_ms must be non-negative")
    return log_event(logger, "timing", {"op": op_name.strip(), "elapsed_ms": round(float(elapsed_ms), 3)})


def with_context(logger: logging.Logger, **ctx: str) -> logging.LoggerAdapter:
    """Wrap a logger in a LoggerAdapter carrying context keys."""
    if not isinstance(logger, logging.Logger):
        raise TypeError("logger must be a logging.Logger")
    return logging.LoggerAdapter(logger, ctx)


def set_level(logger: logging.Logger, level: str | int) -> None:
    """Set the log level on a logger."""
    if isinstance(level, str):
        lvl = getattr(logging, level.upper(), None)
        if not isinstance(lvl, int):
            raise ValueError(f"Unknown log level: {level}")
        logger.setLevel(lvl)
    elif isinstance(level, int):
        logger.setLevel(level)
    else:
        raise TypeError("level must be str or int")


def flush_all() -> int:
    """Flush all registered JsonlLogHandlers and return count flushed."""
    count = 0
    for h in list(_HANDLERS):
        h.flush()
        count += 1
    return count
