#!/usr/bin/env python3

"""Helper module for generating pulse waves flawlessly."""

from math import cos, pi
from datetime import datetime, timedelta
from typing import Tuple


class PulseWave:
    def __init__(self,
                 period_s: timedelta,
                 scale: Tuple[int, int] = (0, 100)):
        self.period_s: timedelta = period_s
        self.scale: Tuple[int, int] = scale
        self.reset()

    def reset(self) -> None:
        self.start_time: datetime = datetime.now()

    def get(self) -> float:
        """Returns the current cosine value as float between 0 and 1."""
        t: timedelta = datetime.now() - self.start_time
        cosine: float = 0.5 * (cos(2 * pi * t / self.period_s) + 1)
        return cosine

    def get_scaled(self) -> int:
        """Returns the current cosine value as scaled integer."""
        return self.get() * (self.scale[1] - self.scale[0]) + self.scale[0]
