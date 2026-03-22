"""Centralized logging setup."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from utils.config import AppConfig


def setup_logger(config: AppConfig) -> logging.Logger:
    """Create or return an initialized application logger."""
    logger = logging.getLogger("canberbyte.docflow")
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, config.log_level.upper(), logging.INFO))

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = RotatingFileHandler(
        config.log_file,
        maxBytes=2_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.propagate = False
    logger.info("Logger initialized for %s", config.app_name)
    return logger
