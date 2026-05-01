"""File-based logger for the daemon.

Writes timestamped events to a rotating log file plus stdout so issues
("pasted twice", "pasted with no selection", etc.) can be diagnosed
after the fact by inspecting the log.

Default path: ~/.typing-assistant/daemon.log
Override with the TYPING_ASSISTANT_LOG environment variable.
"""

from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

_LOGGER_NAME = "typing-assistant"


def _resolve_log_path() -> Path:
    override = os.environ.get("TYPING_ASSISTANT_LOG")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".typing-assistant" / "daemon.log"


def get_logger() -> logging.Logger:
    logger = logging.getLogger(_LOGGER_NAME)
    if getattr(logger, "_ta_configured", False):
        return logger

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    fmt = logging.Formatter(
        "%(asctime)s.%(msecs)03d %(levelname)-5s %(message)s",
        datefmt="%H:%M:%S",
    )

    log_path = _resolve_log_path()
    file_path_str: str | None = None
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_path, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)
        file_path_str = str(log_path)
    except Exception as e:
        sys.stderr.write(
            f"[typing-assistant] could not open log file {log_path}: {e}\n"
        )

    # Reconfigure stdout to utf-8 so Hebrew/emoji don't crash on Windows cp1252.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")  # type: ignore[attr-defined]
    except Exception:
        pass
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(fmt)
    logger.addHandler(stream_handler)

    logger._ta_configured = True  # type: ignore[attr-defined]
    logger._ta_log_path = file_path_str  # type: ignore[attr-defined]
    return logger


def log_path() -> str | None:
    """Return the absolute path of the active log file, or None if file
    logging is unavailable."""
    return getattr(get_logger(), "_ta_log_path", None)
