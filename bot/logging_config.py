"""
Logging configuration for the trading bot.
Sets up both file and console handlers with appropriate formatting.
"""

import logging
import sys
from pathlib import Path

LOG_FILE = "trading_bot.log"
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Configure and return the root logger with file and console handlers.

    Args:
        level: Logging level string (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Configured root logger instance.
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Capture everything; handlers filter

    # Avoid duplicate handlers on re-import
    if root_logger.handlers:
        return logging.getLogger("trading_bot")

    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)

    # ── File handler (DEBUG and above → full detail) ──────────────────────────
    file_handler = logging.FileHandler(Path(LOG_FILE), encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # ── Console handler (INFO and above → clean output) ───────────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    return logging.getLogger("trading_bot")


def get_logger(name: str) -> logging.Logger:
    """
    Return a named child logger under the 'trading_bot' namespace.

    Args:
        name: Sub-module name (e.g. 'client', 'orders')

    Returns:
        Named logger instance.
    """
    return logging.getLogger(f"trading_bot.{name}")
