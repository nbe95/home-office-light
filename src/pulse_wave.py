#!/usr/bin/env python3

"""Helper module for generating pulse waves flawlessly."""

from math import cos, pi
from datetime import datetime, timedelta
from typing import Tuple


class PulseWave:
    def __init__(self,
                 period: timedelta,
                 scale: Tuple[int, int] = (0, 100)):
        self.period: timedelta = period
        self.scale: Tuple[int, int] = scale
        self.reset()

    def reset(self) -> None:
        self.start_time: datetime = datetime.now()

    def get(self) -> float:
        """Returns the current cosine value as float between 0 and 1."""
        t: float = (datetime.now() - self.start_time).total_seconds()
        cosine: float = cos(2 * pi * t / self.period.total_seconds())
        return 0.5 * (cosine + 1)

    def get_scaled(self) -> int:
        """Returns the current cosine value as scaled integer."""
        return int(self.get()) * (self.scale[1] - self.scale[0]) + self.scale[0]
