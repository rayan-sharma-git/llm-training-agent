"""Structured logging setup."""
from __future__ import annotations

import logging
import sys
from enum import LogLevel
from pathlib import Path
from typing import Optional

from core.config import get_settings, LogLevel as ConfigLogLevel


class JsonFormatter(logging.Formatter):
    """Format logs as JSON."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "component": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        return logging.Formatter().formatMessage(record)


def setup_logging() -> None:
    """Configure application logging."""
    settings = get_settings()
    level_map = {
        ConfigLogLevel.DEBUG: logging.DEBUG,
        ConfigLogLevel.INFO: logging.INFO,
        ConfigLogLevel.WARNING: logging.WARNING,
        ConfigLogLevel.ERROR: logging.ERROR,
        ConfigLogLevel.CRITICAL: logging.CRITICAL,
    }
    log_level = level_map.get(settings.log_level, logging.INFO)
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()
    handler = logging.StreamHandler(sys.stdout)
    if settings.log_format == "json":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter("%(timestamp)s %(level)s %(component)s %(message)s"))
    root_logger.addHandler(handler)
    if settings.log_file:
        file_handler = logging.FileHandler(settings.log_file)
        file_handler.setFormatter(JsonFormatter())
        root_logger.addHandler(file_handler)
    for noisy in ("httpx", "httpcore", "sqlalchemy", "uvicorn.access"):
        logging.getLogger(noisy).setLevel(logging.WARNING)