#!/usr/bin/env python3

"""Helper module for easy logger configuration."""

import logging
from sys import stdout

from constants import LOG_LEVEL


def get_logger(name: str, log_level: int = LOG_LEVEL) -> logging.Logger:
    """Set up and return our desired logger."""
    logger: logging.Logger = logging.getLogger(name)
    handler: logging.StreamHandler = logging.StreamHandler(stdout)
    handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(log_level)
    return logger
