"""
Structured logging configuration for OmniDrive CLI.

Provides JSON formatter for machine-readable logs, a colorized console
formatter for human consumption, session-scoped correlation IDs, and
log level control via the OMNIDRIVE_LOG_LEVEL environment variable.
"""
import json
import logging
import os
import sys
import uuid
from datetime import datetime, timezone


class CorrelationIdFilter(logging.Filter):
    """Attach a session-scoped correlation ID to every log record."""

    def __init__(self) -> None:
        super().__init__()
        self.correlation_id = uuid.uuid4().hex[:12]

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = self.correlation_id  # type: ignore[attr-defined]
        return True


class JsonFormatter(logging.Formatter):
    """Emit one JSON object per log line for machine consumption."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "corr_id": getattr(record, "correlation_id", ""),
        }
        if record.exc_info and record.exc_info[0] is not None:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


class ConsoleFormatter(logging.Formatter):
    """Colorized human-readable console formatter (uses click for colors)."""

    _COLORS = {
        logging.DEBUG: "cyan",
        logging.INFO: "green",
        logging.WARNING: "yellow",
        logging.ERROR: "red",
        logging.CRITICAL: "red",
    }

    def format(self, record: logging.LogRecord) -> str:
        try:
            import click

            color = self._COLORS.get(record.levelno, None)
            level = click.style(
                f"{record.levelname:<8}", fg=color, bold=True
            )
        except Exception:
            level = f"{record.levelname:<8}"

        corr = getattr(record, "correlation_id", "")
        corr_tag = f"[{corr}] " if corr else ""
        base = f"{level}{corr_tag}{record.name}: {record.getMessage()}"
        if record.exc_info and record.exc_info[0] is not None:
            base += "\n" + self.formatException(record.exc_info)
        return base


def setup_logging(level: int | str | None = None) -> logging.Logger:
    """Configure the omnidrive root logger.

    Args:
        level: Override log level. Falls back to OMNIDRIVE_LOG_LEVEL env var
               (default ``INFO``).

    Returns:
        The configured ``omnidrive`` logger.
    """
    if level is None:
        env_level = os.environ.get("OMNIDRIVE_LOG_LEVEL", "INFO").upper()
        level = env_level
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)

    logger = logging.getLogger("omnidrive")
    logger.setLevel(level)

    # Avoid duplicate handlers when called multiple times.
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(ConsoleFormatter())
        handler.addFilter(CorrelationIdFilter())
        logger.addHandler(handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the ``omnidrive`` namespace."""
    if not name.startswith("omnidrive"):
        name = f"omnidrive.{name}"
    return logging.getLogger(name)
