#!/usr/bin/env python3

"""Python module to configure various constants."""

import logging
from os import environ as env
from datetime import timedelta as td
from typing import List, Dict


# General
_log_mapping: Dict[str, int] = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}
LOG_LEVEL: int = _log_mapping[env["LOG_LEVEL"]] \
                 if env["LOG_LEVEL"] in _log_mapping else logging.INFO

# Flask
MAIN_TITLE: str = "9Light"
FRONTEND_TEMPLATE_DIR: str = "templates/"
FRONTEND_STATIC_DIR: str = "static/"
PORT_FRONTEND: int = 9080
PORT_BACKEND: int = 9000
PORT_REMOTE: int = 9001

# Bell
BELL_REQUEST_TIMEOUT: td = td(seconds=30)
BELL_DEBOUNCE_TIME: td = td(milliseconds=50)
BELL_BUZZER_SEQUENCE: List[int] = [150, 100, 150, 100, 350]
PIN_BUTTON: int = 23
PIN_BUZZER: int = 24

# LEDS
PIN_LEDS: int = 18
LEDS_TOTAL: int = 13
LEDS_TOP: List[int] = list(range(0, 6))
LEDS_BOTTOM: List[int] = list(range(7, 13))

# Remotes
REMOTE_EXP_TIMEOUT: td = td(hours=3)
