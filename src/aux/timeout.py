#!/usr/bin/env python3

"""Helper module for realizing simple timeouts using threads."""

from threading import Thread
from time import sleep
from datetime import datetime, timedelta
from typing import Callable, Any


class Timeout(Thread):
    """Timeout helper class, which will run a specific task as a thread."""

    def __init__(self, func: Callable[[], Any], timeout: timedelta):
        super().__init__(target=self._run, daemon=True)
        self.func: Callable[[], Any] = func
        self.timeout: timedelta = timeout
        self._canceled: bool = False

    def _run(self) -> None:
        """Start the timeout and when elapsed, run the registered function."""
        end: datetime = datetime.now() + self.timeout
        while datetime.now() < end:
            if self._canceled:
                return
            sleep(0.1)
        self.func()

    def cancel(self) -> None:
        """Cancel this timeout immediately."""
        self._canceled = True
