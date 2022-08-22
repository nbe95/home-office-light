#!/usr/bin/env python3

"""Helper module for easy managing of interruptable background tasks."""

from threading import Thread
from typing import Callable, Optional, Tuple, Any


class BgTask:
    """Helper class for running a specific task in the background."""

    def __init__(self, target: Callable[..., Any],
                 args: Tuple[Any, ...] = ()):
        self.target: Callable[..., Any] = target
        self.args: Tuple[Any, ...] = args
        self.count: int = 0
        self._cancel: bool = False
        self._thread: Optional[Thread] = None

    def cancel(self) -> None:
        """Abort task immediatley."""
        if self._thread:
            self._cancel = True
            self._thread.join()
        self._cancel = False

    def start(self, args: Optional[Tuple[Any, ...]] = None) -> None:
        """Run the specified task. If given, the last arguments will be
        overridden."""
        self.count += 1
        if args:
            self.args = args
        self._thread = Thread(target=self.target, args=self.args, daemon=True)
        self._thread.start()

    def restart(self, args: Optional[Tuple[Any, ...]] = None) -> None:
        """Cancel and immediately (re-)start the task."""
        self.cancel()
        self.start(args)

    def is_running(self) -> bool:
        """Check if the background task is still running."""
        return self._thread is not None and self._thread.is_alive()

    def is_canceled(self) -> bool:
        """Check if the task was canceled.
        Note: When using loops etc., this function must be checked often to
        prevent any deadlocks!"""
        return self._cancel
