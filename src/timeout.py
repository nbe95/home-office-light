#!/usr/bin/env python3

"""Helper module for realizing simple timeouts using threads."""

from threading import Thread
from time import sleep
from datetime import timedelta
from typing import Callable, Any


class Timeout(Thread):
    """Timeout helper class, which will run a specific task as a thread."""

    def __init__(self, func: Callable[[], None], timeout: timedelta):
        super().__init__()
        self.func: Callable[[], Any] = func
        self.timeout: timedelta = timeout
        self._canceled: bool = False
        self.start()

    def run(self) -> None:
        """Start the timeout and when elapsed, run the registered function."""
        sleep(self.timeout.total_seconds())
        if not self._canceled:
            self.func()

    def cancel(self) -> None:
        """Cancel this timeout immediately."""
        self._canceled = True
