from __future__ import annotations

"""Structured logging with correlation IDs."""

import json
import logging
import sys
import uuid
from contextvars import ContextVar
from typing import Any, Optional

_correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")


def get_correlation_id() -> str:
    cid = _correlation_id.get()
    if not cid:
        cid = str(uuid.uuid4())
        _correlation_id.set(cid)
    return cid


def set_correlation_id(cid: str) -> None:
    _correlation_id.set(cid)


class StructuredFormatter(logging.Formatter):
    """JSON log formatter."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "correlation_id": getattr(record, "correlation_id", get_correlation_id()),
        }
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)
        return json.dumps(log_data)


class StructuredLogger:
    """Structured JSON logger."""

    def __init__(self, name: str, level: int = logging.INFO) -> None:
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(StructuredFormatter())
            self.logger.addHandler(handler)

    def info(self, message: str, **kwargs: Any) -> None:
        extra = {"correlation_id": get_correlation_id(), "extra_data": kwargs}
        self.logger.info(message, extra=extra)

    def error(self, message: str, exc: Optional[Exception] = None, **kwargs: Any) -> None:
        extra = {"correlation_id": get_correlation_id(), "extra_data": kwargs}
        self.logger.error(message, extra=extra, exc_info=exc is not None)

    def warning(self, message: str, **kwargs: Any) -> None:
        extra = {"correlation_id": get_correlation_id(), "extra_data": kwargs}
        self.logger.warning(message, extra=extra)

    def debug(self, message: str, **kwargs: Any) -> None:
        extra = {"correlation_id": get_correlation_id(), "extra_data": kwargs}
        self.logger.debug(message, extra=extra)


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance."""
    return StructuredLogger(name)
