#!/usr/bin/env python3

"""Python module to configure various constants."""

import logging
import sys
from datetime import timedelta as td
from os import environ as env
from socket import getfqdn, gethostbyname
from typing import Dict, List

# General
HOSTNAME: str = getfqdn()
IP_ADDR: str = gethostbyname(HOSTNAME)
SW_VERSION: str = str(env["GIT_VERSION"])
PY_VERSION: str = ".".join(list(map(str, sys.version_info[:3])))

# Logging
LOG_MAPPING: Dict[str, int] = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}
LOG_LEVEL: int = LOG_MAPPING.get(env["LOG_LEVEL"], logging.INFO)
LOG_BUFFER_CAPACITY: int = 1000

# Flask
MAIN_TITLE: str = "9light"
MAIN_TITLE_NAVBAR: str = "light"
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
