#!/usr/bin/env python3

"""List of all system states of our 9light."""

from enum import Enum


class States(Enum):
    """Enumeration of all states with corresponding numerical ID."""
    NONE = 0
    CALL = 1
    VIDEO = 2
    REQUEST = 3
    COFFEE = 99
